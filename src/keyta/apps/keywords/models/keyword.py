import re
from html.parser import HTMLParser

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _

from keyta.models.base_model import AbstractBaseModel
from keyta.rf_export.keywords import RFKeyword


class HTML2Text(HTMLParser):
    def __init__(self, *, convert_charrefs = True):
        self.texts = []
        super().__init__(convert_charrefs=convert_charrefs)

    def handle_data(self, data):
        self.texts.append(data)

    def get_text(self):
        return '\n'.join(self.texts)


class KeywordType(models.TextChoices):
    LIBRARY = 'LIBRARY', _('Schlüsselwort aus Bibliothek')
    RESOURCE = 'RESOURCE', _('Schlüsselwort aus Ressource')

    # Customization #
    ACTION = 'ACTION', _('Aktion')
    SEQUENCE = 'SEQUENCE', _('Sequenz')


class Keyword(AbstractBaseModel):
    library = models.ForeignKey(
        'libraries.Library',
        null=True,
        on_delete=models.CASCADE,
        related_name='keywords',
        verbose_name=_('Bibliothek')
    )
    resource = models.ForeignKey(
        'resources.Resource',
        null=True,
        on_delete=models.CASCADE,
        related_name='keywords',
        verbose_name=_('Ressource')
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('Name')
    )
    short_doc = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Beschreibung')
    )
    args_doc = models.TextField(
        blank=True,
        verbose_name=_('Parameters')
    )
    documentation = models.TextField(
        blank=True,
        verbose_name=_('Dokumentation')
    )
    type = models.CharField(
        max_length=255,
        choices=KeywordType.choices
    )

    # ---Customization--
    setup_teardown = models.BooleanField(
        default=False,
        verbose_name=_('Vor-/Nachbereitung')
    )
    windows = models.ManyToManyField(
        'windows.Window',
        related_name='keywords',
        verbose_name=_('Maske')
    )
    systems = models.ManyToManyField(
        'systems.System',
        related_name='keywords',
        verbose_name=_('Systeme')
    )

    def __str__(self):
        return self.name

    @property
    def has_empty_sequence(self):
        return not self.calls.exists()

    @property
    def id_name(self):
        return f'{self.type[0]}{self.id}::{self.name}'

    @property
    def is_action(self):
        return self.type == KeywordType.ACTION

    @property
    def is_sequence(self):
        return self.type == KeywordType.SEQUENCE

    def save(
        self, force_insert=False, force_update=False, using=None,
        update_fields=None
    ):
        self.name = re.sub(r"\s{2,}", " ", self.name)
        super().save(force_insert, force_update, using, update_fields)

    def robot_documentation(self):
        html_parser = HTML2Text()
        html_parser.feed(self.documentation)
        return html_parser.get_text()

    def to_robot(self) -> RFKeyword:
        args = self.parameters.args()
        kwargs = self.parameters.kwargs()
        return_value = self.return_value.first()

        return {
            'name': self.id_name,
            'doc': self.robot_documentation(),
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
