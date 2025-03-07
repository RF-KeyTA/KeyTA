from django.utils.translation import gettext as _

from keyta.models.keyword_source import KeywordSource


class Resource(KeywordSource):
    def is_library(self):
        return False

    class Meta:
        verbose_name = _('Ressource')
        verbose_name_plural = _('Ressourcen')
