from django.db import models

from apps.libraries.models import LibraryImport, LibraryImportType


class ActionLibraryImport(LibraryImport):
    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super().
                get_queryset()
                .only('execution', 'library')
                .filter(type=LibraryImportType.FROM_ACTION)
                .order_by('library__name')
            )

    objects = Manager()

    class Meta:
        proxy = True
        verbose_name = 'Bibliothek-Import'
        verbose_name_plural = 'Bibliothek-Imports'
