from apps.executions.models import SetupTeardown


class TestCaseExecutionSetupTeardown(SetupTeardown):
    class Meta:
        proxy = True
        verbose_name = 'Schlüsselwort-Aufruf'
