from django.db import models
from django.utils.translation import gettext_lazy as _

from keyta.apps.keywords.models.keywordcall import KeywordCall, KeywordCallType


class TestStep(KeywordCall):
    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .only('index', 'testcase', 'window', 'to_keyword')
                .filter(type=KeywordCallType.TEST_STEP)
            )

    objects = Manager()

    def save(
        self, force_insert=False, force_update=False,
        using=None, update_fields=None
    ):
        self.type = KeywordCallType.TEST_STEP
        return super().save(force_insert, force_update, using, update_fields)

    class Meta:
        proxy = True
        verbose_name = _('Schritt')
        verbose_name_plural = _('Schritte')
