from django.db import models
from django.utils.translation import gettext as _

from apps.keywords.models import KeywordCall, KeywordCallType


class KeywordExecutionCall(KeywordCall):
    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .filter(type=KeywordCallType.KEYWORD_EXECUTION)
            )

    objects = Manager()

    def save(
        self, force_insert=False, force_update=False,
        using=None, update_fields=None
    ):
        self.type = KeywordCallType.KEYWORD_EXECUTION
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        proxy = True
        verbose_name = _('Aufrufparameter')
