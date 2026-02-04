from django.contrib import admin
from django.contrib.admin import StackedInline
from django.utils.translation import gettext_lazy as _

from ..forms import SetupTeardownFormset
from ..models import TestCaseExecution, UserExecution
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

    def has_change_permission(self, request, obj=None):
        return self.can_change(request.user, 'testcase')


class TestTeardownInline(TeardownInline):
    verbose_name_plural = _('Testnachbereitung')

    def has_change_permission(self, request, obj=None):
        return self.can_change(request.user, 'testcase')


class UserExecutionInline(StackedInline):
    model = UserExecution
    fields = ['stop_on_failure']
    max_num = 1
    template = 'execution_user_settings.html'
    verbose_name_plural = ''

    def get_queryset(self, request):
        return super().get_queryset(request).filter(user=request.user)

    def has_change_permission(self, request, obj=None):
        return True


@admin.register(TestCaseExecution)
class TestCaseExecutionAdmin(ExecutionAdmin):
    inlines = [
        TestSetupInline,
        TestTeardownInline
    ]

    def get_inlines(self, request, obj):
        UserExecution.objects.get_or_create(
            execution=obj,
            user=request.user
        )

        return super().get_inlines(request, obj) + [UserExecutionInline]
