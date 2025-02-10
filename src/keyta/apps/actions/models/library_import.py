from django.db import models
from django.utils.translation import gettext as _

from keyta.apps.libraries.models import LibraryImport, LibraryImportType


class ActionLibraryImport(LibraryImport):
    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super().
                get_queryset()
                .only('library')
                .filter(type=LibraryImportType.FROM_ACTION)
                .order_by('library__name')
            )

    objects = Manager()

    class Meta:
        proxy = True
        verbose_name = _('Bibliothek-Import')
        verbose_name_plural = _('Bibliothek-Imports')
