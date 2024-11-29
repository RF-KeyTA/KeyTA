from django.db import models

from apps.common.abc import AbstractBaseModel


__all__ = ['Library', 'LibraryInitDocumentation']


class Library(AbstractBaseModel):
    name = models.CharField(max_length=255, unique=True, verbose_name='Name')
    version = models.CharField(max_length=255)
    init_doc = models.TextField(verbose_name='Einrichtung')
    documentation = models.TextField(verbose_name='Dokumentation')

    def __str__(self):
        return self.name

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


    class Meta:
        verbose_name = 'Bibliothek'
        verbose_name_plural = 'Bibliotheken'


class LibraryInitDocumentation(Library):
    class Meta:
        proxy = True
