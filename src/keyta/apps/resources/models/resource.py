from django.db import models
from django.utils.translation import gettext as _

from keyta.models.keyword_source import KeywordSource


class Resource(KeywordSource):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))
    documentation = models.TextField(verbose_name=_('Dokumentation'))

    def __str__(self):
        return self.name

    def is_library(self):
        return False

    class Meta:
        verbose_name = _('Ressource')
        verbose_name_plural = _('Ressourcen')
