from django.db import models

from apps.keywords.models import Keyword
from apps.keywords.models.keyword import KeywordType

__all__ = ['ResourceKeyword', 'ResourceKeywordDocumentation']


class ResourceKeyword(Keyword):
    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .only('resource', 'name', 'short_doc', 'documentation')
                .filter(type=KeywordType.RESOURCE)
                .order_by('name')
            )

    objects = Manager()

    def save(
        self, force_insert=False, force_update=False,
        using=None, update_fields=None
    ):
        self.type = KeywordType.RESOURCE
        return super().save(force_insert, force_update, using, update_fields)

    class Meta:
        proxy = True
        verbose_name = 'Ressource-Schlüsselwort'
        verbose_name_plural = 'Ressource-Schlüsselwörter'


class ResourceKeywordDocumentation(ResourceKeyword):
    class Meta:
        proxy = True
        verbose_name = 'Dokumentation des Ressource-Schlüsselworts'
