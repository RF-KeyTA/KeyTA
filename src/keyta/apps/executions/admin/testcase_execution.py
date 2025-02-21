from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.apps.executions.admin.execution import ExecutionAdmin

from ..models import TestCaseExecution
from .setup_teardown_inline import SetupInline, TeardownInline


class TestSetupInline(SetupInline):
    verbose_name_plural = _('Testvorbereitung')


class TestTeardownInline(TeardownInline):
    verbose_name_plural = _('Testnachbereitung')


@admin.register(TestCaseExecution)
class TestCaseExecutionAdmin(ExecutionAdmin):
    inlines = [
        TestSetupInline,
        TestTeardownInline
    ]
