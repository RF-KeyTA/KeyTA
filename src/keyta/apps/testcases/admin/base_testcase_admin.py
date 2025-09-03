from django.forms import ModelMultipleChoiceField
from django.utils.translation import gettext_lazy as _

from adminsortable2.admin import SortableAdminBase
from model_clone import CloneModelAdminMixin

from keyta.admin.base_admin import BaseAdmin
from keyta.admin.field_documentation import DocumentationField
from keyta.admin.list_filters import SystemListFilter
from keyta.apps.executions.admin import ExecutionInline
from keyta.apps.executions.models import TestCaseExecution
from keyta.apps.keywords.admin import TestStepsInline
from keyta.apps.systems.models import System
from keyta.widgets import CustomCheckboxSelectMultiple

from ..models import TestCase


class LocalExecution(ExecutionInline):
    model = TestCaseExecution


class BaseTestCaseAdmin(DocumentationField, CloneModelAdminMixin, SortableAdminBase, BaseAdmin):
    list_display = ['name', 'description']
    list_display_links = ['name']
    list_filter = [
        ('systems', SystemListFilter),
    ]
    search_fields = ['name']
    search_help_text = _('Name')

    fields = [
        'systems',
        'name',
        'description',
    ]
    inlines = [
        TestStepsInline,
        LocalExecution
    ]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'systems':
            field = ModelMultipleChoiceField(
                widget=CustomCheckboxSelectMultiple,
                queryset=System.objects
            )

            if testcase_id := request.resolver_match.kwargs.get('object_id'):
                testcase = TestCase.objects.get(id=testcase_id)
                testcase_systems = testcase.systems.values_list('pk', flat=True)
                teststep_systems = testcase.steps.values_list('window__systems', flat=True)
                field.widget.in_use = set(testcase_systems).intersection(teststep_systems)

        return field

    def get_inlines(self, request, obj):
        testcase: TestCase = obj

        if not testcase:
            return []

        if testcase.has_empty_sequence:
            return [TestStepsInline]

        return self.inlines

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        testcase: TestCase = obj

        if not change:
            form.save_m2m()
            testcase.create_execution()
