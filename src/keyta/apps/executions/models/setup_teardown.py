from django.db import models
from django.utils.translation import gettext_lazy as _

from keyta.apps.keywords.models import KeywordCall
from keyta.apps.keywords.models.keywordcall import TestSetupTeardown


class Setup(KeywordCall):
    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .only('execution', 'to_keyword')
                .filter(type=TestSetupTeardown.TEST_SETUP)
            )

    objects = Manager()

    def save(
        self, force_insert=False, force_update=False,
        using=None, update_fields=None
    ):
        if not self.pk:
            self.index = 1
            self.type = TestSetupTeardown.TEST_SETUP

        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        proxy = True
        verbose_name = _('Vorbereitung')
        verbose_name_plural = _('Vorbereitung')


class Teardown(KeywordCall):
    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .only('execution', 'to_keyword')
                .filter(type=TestSetupTeardown.TEST_TEARDOWN)
            )

    objects = Manager()

    def save(
        self, force_insert=False, force_update=False,
        using=None, update_fields=None
    ):
        self.type = TestSetupTeardown.TEST_TEARDOWN
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        proxy = True
        verbose_name = _('Nachbereitung')
        verbose_name_plural = _('Nachbereitung')
