from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext as _

from apps.executions.admin import (
    ExecutionAdmin,
    LibraryImportsInline,
    ResourceImportsInline,
    ExecutionInline,
    SetupTeardownInline
)
from apps.executions.models import TestCaseExecutionSetupTeardown
from apps.keywords.models import TestSetupTeardown

from ..models import TestCaseExecution


class TestCaseExecutionInline(ExecutionInline):
    model = TestCaseExecution


class TestSetupTeardownInline(SetupTeardownInline):
    model = TestCaseExecutionSetupTeardown
    extra = 0
    max_num = 2
    verbose_name = _('Vor- oder Nachbereitung')
    verbose_name_plural = _('Vorbereitung und Nachbereitung')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'type':
            field.label = _('Vor/Nachbereitung')
            field.widget.choices = TestSetupTeardown.choices

        return field


@admin.register(TestCaseExecution)
class TestCaseExecutionAdmin(ExecutionAdmin):
    change_form_template = 'admin/setup_teardown/change_form.html'
    inlines = [
        LibraryImportsInline,
        ResourceImportsInline,
        TestSetupTeardownInline
    ]

    def change_view(self, request: HttpRequest, object_id, form_url="",
                    extra_context=None):
        context = {
            'get_execution': lambda: TestCaseExecution.objects.get(id=object_id)
        }

        return super().change_view(request, object_id, form_url, context)
