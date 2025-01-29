from django.utils.translation import gettext as _

from keyta.apps.keywords.models import TestSetupTeardown

from .setup_teardown import SetupTeardown


class KeywordExecutionSetup(SetupTeardown):
    def save(
        self, force_insert=False, force_update=False,
        using=None, update_fields=None
    ):
        self.type = TestSetupTeardown.TEST_SETUP
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        proxy = True
        verbose_name = _('Schlüsselwort-Aufruf')
