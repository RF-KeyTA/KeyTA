import os
import sys
from typing import Optional

from django.db import models
from django.utils.translation import gettext as _

from keyta.models.keyword_source import KeywordSource


class Resource(KeywordSource):
    path = models.CharField(
        max_length=255,
        unique=True
    )

    def is_library(self):
        return False

    @classmethod
    def resource_file_not_found(cls, filepath: str) -> Optional[str]:
        resource_exists = any(
            os.path.isfile(os.path.normpath(os.path.join(path, filepath)))
            for path in sys.path 
            if os.path.isdir(path)
        )

        if not resource_exists:
            return _(f'Die Ressource "{filepath}" ist nicht im PYTHONPATH vorhanden.')
        
        return None

    class Meta(KeywordSource.Meta):
        verbose_name = _('Ressource')
        verbose_name_plural = _('Ressourcen')
