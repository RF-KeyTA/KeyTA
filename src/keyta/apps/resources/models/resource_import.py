from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _

from keyta.models.base_model import AbstractBaseModel
from keyta.rf_export.settings import RFResourceImport


__all__ = ['ResourceImport', 'ResourceImportType']


class ResourceImportType(models.TextChoices):
    FROM_EXECUTION = 'FROM_EXECUTION', _('Aus einer Ausführung')
    FROM_WINDOW = 'FROM_WINDOW', _('Aus einer Maske')


class ResourceImport(AbstractBaseModel):
    execution = models.ForeignKey(
        'executions.Execution',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        blank=True,
        related_name='resource_imports'
    )
    window = models.ForeignKey(
        'windows.Window',
        null=True,
        default=None,
        blank=True,
        on_delete=models.CASCADE,
        related_name='resource_imports'
    )
    resource = models.ForeignKey(
        'resources.Resource',
        on_delete=models.CASCADE,
        verbose_name=_('Ressource')
    )
    type = models.CharField(max_length=255, choices=ResourceImportType.choices)

    def __str__(self):
        return f'{self.execution or self.window} -> {self.resource}'

    def save(
        self, force_insert=False, force_update=False, using=None,
            update_fields=None
    ):
        if not self.pk:
            if self.window:
                self.type = ResourceImportType.FROM_WINDOW
            if self.execution:
                self.type = ResourceImportType.FROM_EXECUTION

            super().save(force_insert, force_update, using, update_fields)
        else:
            super().save(force_insert, force_update, using, update_fields)

    def to_robot(self, user: Optional[AbstractUser]=None) -> RFResourceImport:
        return {
            'resource': self.resource.path,
        }

    class QuerySet(models.QuerySet):
        def resource_ids(self):
            return self.values_list('resource', flat=True).distinct()

    objects = QuerySet.as_manager()

    class Meta:
        ordering = ['resource__name']
        verbose_name = _('Ressource-Import')
        verbose_name_plural = _('Ressource-Imports')
        constraints = [
            models.CheckConstraint(
                name='resource_import_sum_type',
                check=
                (Q(type=ResourceImportType.FROM_EXECUTION) &
                 Q(execution__isnull=False) &
                 Q(window__isnull=True))
                |
                (Q(type=ResourceImportType.FROM_WINDOW) &
                 Q(execution__isnull=True) &
                 Q(window__isnull=False))
            ),
            models.UniqueConstraint(
                name='unique_execution_resource_import',
                condition=Q(execution__isnull=False),
                fields=['execution', 'resource'],
            ),
            models.UniqueConstraint(
                name='unique_window_resource_import',
                condition=Q(window__isnull=False),
                fields=['window', 'resource'],
            )
        ]
