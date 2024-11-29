import re
from xml.etree import ElementTree

from django.db import models
from django.db.models import Q

from apps.common.abc import AbstractBaseModel
from apps.rf_export.keywords import RFKeyword


class KeywordType(models.TextChoices):
    LIBRARY = 'LIBRARY', 'Schlüsselwort aus Bibliothek'
    RESOURCE = 'RESOURCE', 'Schlüsselwort aus Ressource'

    # Customization #
    ACTION = 'ACTION', 'Aktion'
    SEQUENCE = 'SEQUENCE', 'Sequenz'


class Keyword(AbstractBaseModel):
    library = models.ForeignKey(
        'libraries.Library',
        null=True,
        on_delete=models.CASCADE,
        related_name='keywords',
        verbose_name='Bibliothek'
    )
    resource = models.ForeignKey(
        'resources.Resource',
        null=True,
        on_delete=models.CASCADE,
        related_name='keywords',
        verbose_name='Ressource'
    )
    name = models.CharField(max_length=255, verbose_name='Name')
    short_doc = models.CharField(max_length=255, blank=True,
                                 verbose_name='Beschreibung')
    args_doc = models.TextField(blank=True, verbose_name='Parameter')
    documentation = models.TextField(blank=True, verbose_name='Dokumentation')
    type = models.CharField(max_length=255, choices=KeywordType.choices)

    # ---Customization--
    everywhere = models.BooleanField(
        default=False,
        verbose_name='In allen Masken'
    )
    setup_teardown = models.BooleanField(
        default=False,
        verbose_name='Vor-/Nachbereitung'
    )
    windows = models.ManyToManyField(
        'windows.Window',
        related_name='keywords',
        verbose_name='Maske'
    )
    systems = models.ManyToManyField(
        'systems.System',
        related_name='keywords',
        verbose_name='Systeme'
    )

    def __str__(self):
        return self.name

    @property
    def has_empty_sequence(self):
        return not self.calls.exists()

    @property
    def id_name(self):
        return f'{self.type[0]}{self.id}::{self.name}'

    def save(
        self, force_insert=False, force_update=False, using=None,
        update_fields=None
    ):
        self.name = re.sub(r"\s{2,}", " ", self.name)
        super().save(force_insert, force_update, using, update_fields)

    def to_robot(self) -> RFKeyword:
        args = self.parameters.args()
        kwargs = self.parameters.kwargs()
        return_value = self.return_value.first()

        return {
            'name': self.id_name,
            'doc': ''.join(ElementTree.XML('<doc>' + self.documentation + '</doc>').itertext()),
            'args': [arg.name for arg in args],
            'kwargs': {kwarg.name: kwarg.default_value for kwarg in kwargs},
            'steps': [
                step.to_robot()
                for step in self.calls.all()
                if step.enabled
            ],
            'return_value': f'${{{return_value}}}' if return_value else None
        }

    @property
    def unique_name(self):
        if self.library:
            return f'{self.library.name}.{self.name}'

        if self.resource:
            return f'{self.resource.name}.{self.name}'

        return self.id_name

    # Customization #
    class QuerySet(models.QuerySet):
        def actions(self):
            return self.filter(type=KeywordType.ACTION)

        def sequences(self):
            return self.filter(type=KeywordType.SEQUENCE)

    objects = QuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["library", "name"],
                name="unique_keyword_per_library"
            ),
            models.UniqueConstraint(
                fields=["resource", "name"],
                name="unique_keyword_per_resource"
            ),

            # Customization #
            models.CheckConstraint(
                name='keyword_sum_type',
                check=
                (Q(type=KeywordType.LIBRARY) &
                 Q(library__isnull=False) &
                 Q(resource__isnull=True))
                |
                (Q(type=KeywordType.RESOURCE) &
                 Q(resource__isnull=False) &
                 Q(library__isnull=True))

                # Customization #
                |
                (Q(type=KeywordType.ACTION) &
                 Q(library__isnull=True) &
                 Q(resource__isnull=True))
                |
                (Q(type=KeywordType.SEQUENCE) &
                 Q(library__isnull=True) &
                 Q(resource__isnull=True))
            )
        ]


class KeywordDocumentation(Keyword):
    class Meta:
        proxy = True
