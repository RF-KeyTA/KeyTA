from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.apps.executions.admin.execution import ExecutionAdmin

from ..models import TestCaseExecution
from .setup_teardown_inline import SetupInline, TeardownInline


class TestSetupInline(SetupInline):
    max_num = 2
    verbose_name_plural = _('Testvorbereitung')


class TestTeardownInline(TeardownInline):
    verbose_name_plural = _('Testnachbereitung')


@admin.register(TestCaseExecution)
class TestCaseExecutionAdmin(ExecutionAdmin):
    inlines = [
        TestSetupInline,
        TestTeardownInline
    ]

    def has_change_permission(self, request, obj=None):
        return self.can_change(request.user, 'testcase')
