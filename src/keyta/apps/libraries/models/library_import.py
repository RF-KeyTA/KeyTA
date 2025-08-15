from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from keyta.models.base_model import AbstractBaseModel
from keyta.rf_export.settings import RFLibraryImport


__all__ = ['LibraryImport', 'LibraryImportType']


class LibraryImportType(models.TextChoices):
    FROM_EXECUTION = 'FROM_EXECUTION', _('Aus einer Ausführung')
    FROM_ACTION = 'FROM_ACTION', _('Aus einer Aktion')


class LibraryImport(AbstractBaseModel):
    execution = models.ForeignKey(
        'executions.Execution',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        blank=True,
        related_name='library_imports'
    )
    keyword = models.ForeignKey(
        'keywords.Keyword',
        null=True,
        default=None,
        blank=True,
        on_delete=models.CASCADE,
        related_name='library_imports'
    )
    library = models.ForeignKey(
        'libraries.Library',
        on_delete=models.PROTECT,
        verbose_name=_('Bibliothek')
    )
    type = models.CharField(max_length=255, choices=LibraryImportType.choices)

    def __str__(self):
        if self.execution:
            return _('Ausführung') + f' {self.execution} -> {self.library}'

        return f'{self.keyword} -> {self.library}'

    def add_parameters(self, user: Optional[AbstractUser]=None):
        for kwarg in self.library.kwargs.all():
            self.kwargs.get_or_create(
                library_import=self,
                user=user,
                library_parameter=kwarg,
                defaults={
                    'value': kwarg.value,
                }
            )

    def save(
        self, force_insert=False, force_update=False, using=None,
            update_fields=None
    ):
        if not self.pk:
            if self.keyword:
                self.type = LibraryImportType.FROM_ACTION
            if self.execution:
                self.type = LibraryImportType.FROM_EXECUTION

            super().save(force_insert, force_update, using, update_fields)

            if not self.execution:
                self.add_parameters()
        else:
            super().save(force_insert, force_update, using, update_fields)

    def to_robot(self, user: Optional[AbstractUser]=None) -> RFLibraryImport:
        kwargs = self.kwargs.filter(user=user).all()

        return {
            'library': str(self.library),
            'kwargs': {str(kwarg): kwarg.value for kwarg in kwargs}
        }

    class QuerySet(models.QuerySet):
        def library_ids(self):
            return self.values_list('library', flat=True).distinct()

    objects = QuerySet.as_manager()

    class Meta:
        ordering = ['library__name']
        verbose_name = _('Bibliothek-Import')
        verbose_name_plural = _('Bibliothek-Imports')
        constraints = [
            models.UniqueConstraint(
                name='unique_execution_library_import',
                condition=Q(execution__isnull=False),
                fields=['execution', 'library'],
            ),
            models.UniqueConstraint(
                name='unique_keyword_library_import',
                condition=Q(keyword__isnull=False),
                fields=['keyword', 'library'],
            )
        ]
