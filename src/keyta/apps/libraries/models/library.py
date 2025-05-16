from django.db import models
from django.utils.translation import gettext_lazy as _

from keyta.models.keyword_source import KeywordSource


class Library(KeywordSource):
    version = models.CharField(
        max_length=255
    )
    init_doc = models.TextField(
        verbose_name=_('Einrichtung')
    )

    ROBOT_LIBRARIES = {
        'BuiltIn',
        'Collections',
        'DateTime',
        'Dialogs',
        'OperatingSystem',
        'Process',
        'Remote',
        'Screenshot',
        'String',
        'Telnet',
        'XML'
    }

    @property
    def has_parameters(self):
        return self.kwargs.exists()

    def is_library(self):
        return True

    class Meta(KeywordSource.Meta):
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_library_name')
        ]
        verbose_name = _('Bibliothek')
        verbose_name_plural = _('Bibliotheken')


class LibraryInitDocumentation(Library):
    class Meta:
        proxy = True
