from typing import Optional
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _

from apps.common.abc import AbstractBaseModel
from apps.rf_export.settings import RFResourceImport

from .resource import Resource


__all__ = ['ResourceImport', 'ResourceImportType']


class ResourceImportType(models.TextChoices):
    FROM_EXECUTION = 'FROM_EXECUTION', _('Aus einer Ausführung')
    FROM_SEQUENCE = 'FROM_SEQUENCE', _('Aus einer Sequenz')


class ResourceImport(AbstractBaseModel):
    execution = models.ForeignKey(
        'executions.Execution',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        blank=True,
        related_name='resource_imports'
    )
    keyword = models.ForeignKey(
        'keywords.Keyword',
        null=True,
        default=None,
        blank=True,
        on_delete=models.CASCADE,
        related_name='resource_imports'
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        verbose_name='Ressource'
    )
    type = models.CharField(max_length=255, choices=ResourceImportType.choices)

    def __str__(self):
        return f'{self.keyword} -> {self.resource}'

    def save(
        self, force_insert=False, force_update=False, using=None,
            update_fields=None
    ):
        if not self.pk:
            if self.keyword:
                self.type = ResourceImportType.FROM_SEQUENCE
            if self.execution:
                self.type = ResourceImportType.FROM_EXECUTION

            super().save(force_insert, force_update, using, update_fields)
        else:
            super().save(force_insert, force_update, using, update_fields)

    def to_robot(self, user: Optional[User]=None) -> RFResourceImport:
        return {
            'resource': str(self.resource),
        }

    class QuerySet(models.QuerySet):
        def resource_ids(self):
            return self.values_list('resource', flat=True)

    objects = QuerySet.as_manager()

    class Meta:
        verbose_name = _('Ressource-Import')
        verbose_name_plural = _('Ressource-Imports')
        constraints = [
            models.CheckConstraint(
                name='resource_import_sum_type',
                check=
                (Q(type=ResourceImportType.FROM_EXECUTION) &
                 Q(execution__isnull=False) &
                 Q(keyword__isnull=True))
                |
                (Q(type=ResourceImportType.FROM_SEQUENCE) &
                 Q(execution__isnull=True) &
                 Q(keyword__isnull=False))
            ),
            models.UniqueConstraint(
                name='unique_execution_resource_import',
                condition=Q(execution__isnull=False),
                fields=['execution', 'resource'],
            ),
            models.UniqueConstraint(
                name='unique_keyword_resource_import',
                condition=Q(keyword__isnull=False),
                fields=['keyword', 'resource'],
            )
        ]
