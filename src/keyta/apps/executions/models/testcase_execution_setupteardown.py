from django.utils.translation import gettext as _

from apps.executions.models import SetupTeardown


class TestCaseExecutionSetupTeardown(SetupTeardown):
    class Meta:
        proxy = True
        verbose_name = _('Schlüsselwort-Aufruf')
