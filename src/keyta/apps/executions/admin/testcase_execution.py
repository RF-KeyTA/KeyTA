from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..forms import SetupTeardownFormset
from ..models import TestCaseExecution
from .execution import ExecutionAdmin
from .setup_teardown_inline import SetupInline, TeardownInline


class TestSetupTeardownFormset(SetupTeardownFormset):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        if index == 0:
            enabled_field = form.fields['enabled']
            enabled_field.disabled = True
            to_keyword_field = form.fields['to_keyword']
            to_keyword_field.disabled = True


class TestSetupInline(SetupInline):
    formset = TestSetupTeardownFormset
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
