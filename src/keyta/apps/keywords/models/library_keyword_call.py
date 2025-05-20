from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from ..models import KeywordCall, KeywordType


class LibraryKeywordCall(KeywordCall):
    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .only('index', 'from_keyword', 'to_keyword')
                .filter(from_keyword__type=KeywordType.ACTION)
            )

    objects = Manager()

    def get_previous_return_values(self) -> QuerySet:
        return (
            super().get_previous_return_values()
            .filter(return_value__isnull=True)
            .exclude(name__isnull=True)
        )

    class Meta:
        proxy = True
        verbose_name = _('Schritt')
        verbose_name_plural = _('Schritte')
