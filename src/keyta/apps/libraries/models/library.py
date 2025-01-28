from django.db import models
from django.utils.translation import gettext as _

from keyta.models.base_model import AbstractBaseModel


__all__ = ['Library', 'LibraryInitDocumentation']


class Library(AbstractBaseModel):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))
    version = models.CharField(max_length=255)
    init_doc = models.TextField(verbose_name=_('Einrichtung'))
    documentation = models.TextField(verbose_name=_('Dokumentation'))

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
        verbose_name = _('Bibliothek')
        verbose_name_plural = _('Bibliotheken')


class LibraryInitDocumentation(Library):
    class Meta:
        proxy = True
