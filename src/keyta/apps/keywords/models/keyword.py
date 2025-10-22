import re

from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from keyta.models.base_model import AbstractBaseModel
from keyta.models.documentation_mixin import DocumentationMixin
from keyta.rf_export.keywords import RFKeyword

from .keywordcall import ExecutionState


class KeywordType(models.TextChoices):
    LIBRARY = 'LIBRARY', _('Schlüsselwort aus Bibliothek')
    RESOURCE = 'RESOURCE', _('Schlüsselwort aus Ressource')

    # Customization #
    ACTION = 'ACTION', _('Aktion')
    SEQUENCE = 'SEQUENCE', _('Sequenz')


class Keyword(DocumentationMixin, AbstractBaseModel):
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

        if not self.pk:
            if self.library:
                self.type = KeywordType.LIBRARY

            if self.resource:
                self.type = KeywordType.RESOURCE

        super().save(force_insert, force_update, using, update_fields)

    def to_robot(self, get_variable_value, in_execution=False) -> RFKeyword:
        args = self.parameters.args()
        kwargs = self.parameters.kwargs()
        return_values = self.return_values.all()
        execute_from = 0
        execute_until = self.calls.count()

        if in_execution:
            if execute_step := self.calls.filter(execution_state=ExecutionState.BEGIN_EXECUTION).first():
                execute_from = execute_step.index

            if execute_step := self.calls.filter(execution_state=ExecutionState.END_EXECUTION).first():
                execute_until = execute_step.index

        steps = (
            self.calls
            .filter(index__gte=execute_from)
            .filter(index__lte=execute_until)
            .exclude(execution_state=ExecutionState.DO_NOT_EXECUTE)
        )

        return {
            'name': self.id_name,
            'doc': self.robot_documentation() + '?steps_tab',
            'args': [arg.name for arg in args],
            'kwargs': {kwarg.name: kwarg.default_value for kwarg in kwargs},
            'steps': [
                step.to_robot(get_variable_value)
                for step in steps
            ],
            'return_values': [f'${{{return_value}}}' for return_value in return_values]
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
        ordering = [Lower('name')]
        constraints = [
            models.UniqueConstraint(
                fields=["library", "name"],
                condition=Q(library__isnull=False),
                name="unique_keyword_per_library"
            ),
            models.UniqueConstraint(
                fields=["resource", "name"],
                condition=Q(resource__isnull=False),
                name="unique_keyword_per_resource"
            )
        ]
        verbose_name = _('Schlüsselwort')
        verbose_name_plural = _('Schlüsselwörter')


class KeywordDocumentation(Keyword):
    class Meta:
        proxy = True
