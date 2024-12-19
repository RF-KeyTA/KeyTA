from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _

from apps.keywords.models import KeywordCall
from apps.keywords.models.keywordcall import TestSetupTeardown, SuiteSetupTeardown


class SetupTeardown(KeywordCall):
    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .only('execution', 'to_keyword')
                .filter(
                    Q(type=TestSetupTeardown.TEST_SETUP) |
                    Q(type=TestSetupTeardown.TEST_TEARDOWN) |
                    Q(type=SuiteSetupTeardown.SUITE_SETUP) |
                    Q(type=SuiteSetupTeardown.SUITE_TEARDOWN)
                )
            )

    objects = Manager()

    class Meta:
        proxy = True
        verbose_name = _('Vor-/Nachbereitung')
