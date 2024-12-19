from django.db import models
from django.utils.translation import gettext as _

from apps.libraries.models import LibraryImport, LibraryImportType


class ExecutionLibraryImport(LibraryImport):
    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super().
                get_queryset()
                .only('execution', 'library')
                .filter(type=LibraryImportType.FROM_EXECUTION)
                .order_by('library__name')
            )

    objects = Manager()

    class Meta:
        proxy = True
        verbose_name = _('Bibliothek-Import')
        verbose_name_plural = _('Bibliothek-Imports')
