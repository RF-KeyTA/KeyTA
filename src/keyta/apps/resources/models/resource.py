import os
import sys
from typing import Optional

from django.utils.translation import gettext as _

from keyta.models.keyword_source import KeywordSource


class Resource(KeywordSource):
    def is_library(self):
        return False

    @classmethod
    def resource_file_not_found(cls, filename: str) -> Optional[str]:
        resource_exists = any(
            os.path.isfile(os.path.normpath(os.path.join(path, filename)))
            for path in sys.path 
            if os.path.isdir(path)
        )

        if not resource_exists:
            return _(f'Die Ressource "{filename}" ist im PYTHONPATH nicht vorhanden.')
        
        return None

    class Meta:
        verbose_name = _('Ressource')
        verbose_name_plural = _('Ressourcen')
