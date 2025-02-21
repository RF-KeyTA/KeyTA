from django.contrib import admin
from django.db.models.functions import Lower
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext as _

from adminsortable2.admin import SortableAdminBase
from model_clone import CloneModelAdminMixin

from keyta.apps.keywords.admin import TestStepsInline
from keyta.apps.executions.admin import ExecutionInline
from keyta.apps.executions.models import TestCaseExecution
from keyta.models.testcase import AbstractTestCase
from keyta.rf_export.rfgenerator import gen_testsuite
from keyta.widgets import BaseSelectMultiple

from .base_admin import BaseAdmin


class LocalExecution(ExecutionInline):
    model = TestCaseExecution


class BaseTestCaseAdmin(CloneModelAdminMixin, SortableAdminBase, BaseAdmin):
    list_display = [
        'system_list', 'name', 'description'
    ]
    list_display_links = ['name']
    list_filter = ['systems']
    search_fields = ['name']
    search_help_text = _('Name')
    ordering = [Lower('name')]


    @admin.display(description=_('Systeme'))
    def system_list(self, obj: AbstractTestCase):
        return list(obj.systems.values_list('name', flat=True))

    fields = [
        'systems',
        'name',
        'description',
        'documentation'
    ]
    inlines = [
        TestStepsInline,
        LocalExecution
    ]

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        if 'export' in request.GET:
            testcase_exec = TestCaseExecution.objects.get(testcase_id=object_id)
            testcase_exec.update_library_imports(request.user)
            testcase_exec.update_resource_imports()
            testsuite = testcase_exec.get_rf_testsuite(request.user)
            robot_file = testsuite['name'] + '.robot'

            return HttpResponse(
                gen_testsuite(testsuite), 
                headers={
                    'Content-Type': 'text/plain', 
                    'Content-Disposition': f'attachment; filename="{robot_file}"'
                }
            )

        return super().change_view(request, object_id, form_url, extra_context)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'systems':
            field.widget = BaseSelectMultiple(_('Systeme hinzufügen'))

        return field

    def get_inlines(self, request, obj):
        testcase: AbstractTestCase = obj

        if not testcase:
            return []

        if testcase.has_empty_sequence:
            return [TestStepsInline]

        return self.inlines

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        testcase: AbstractTestCase = obj

        if not change:
            form.save_m2m()
            testcase.create_execution()
