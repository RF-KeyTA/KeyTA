from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .keywordcall import KeywordCall, KeywordCallType


class ExecutionKeywordCall(KeywordCall):
    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .filter(type=KeywordCallType.KEYWORD_EXECUTION)
            )

    objects = Manager()

    def has_empty_arg(self, user: Optional[AbstractUser]=None):
        if not self.parameters.exists():
            return True

        return super().has_empty_arg(user)

    def save(
        self, force_insert=False, force_update=False,
        using=None, update_fields=None
    ):
        self.type = KeywordCallType.KEYWORD_EXECUTION
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        proxy = True
        verbose_name = _('Eingabewerte')
