from django.db import models

from apps.keywords.models import Keyword
from apps.keywords.models.keyword import KeywordType

__all__ = ['LibraryKeyword', 'LibraryKeywordDocumentation']


class LibraryKeyword(Keyword):
    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .only('library', 'name', 'short_doc', 'documentation')
                .filter(type=KeywordType.LIBRARY)
                .order_by('name')
            )

    objects = Manager()

    def save(
        self, force_insert=False, force_update=False,
        using=None, update_fields=None
    ):
        self.type = KeywordType.LIBRARY
        return super().save(force_insert, force_update, using, update_fields)

    class Meta:
        proxy = True
        verbose_name = 'Bibliothek-Schlüsselwort'
        verbose_name_plural = 'Bibliothek-Schlüsselwörter'


class LibraryKeywordDocumentation(LibraryKeyword):
    class Meta:
        proxy = True
        verbose_name = 'Dokumentation des Bibliothek-Schlüsselworts'
