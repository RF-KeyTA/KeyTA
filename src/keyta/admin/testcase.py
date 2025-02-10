from django.contrib import admin
from django.db.models.functions import Lower
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext as _

from adminsortable2.admin import SortableAdminBase
from model_clone import CloneModelAdminMixin

from keyta.admin.base_admin import BaseAdmin
from keyta.apps.teststeps.inline import TestSteps
from keyta.models.testcase import AbstractTestCase
from keyta.widgets import BaseSelectMultiple
from keyta.rf_export.rfgenerator import gen_testsuite

from keyta.apps.executions.admin import ExecutionInline
from keyta.apps.executions.models import TestCaseExecution


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

    change_form_template = 'admin/testcase/change_form.html'
    fields = [
        'systems',
        'name',
        'description',
        'documentation'
    ]
    inlines = [
        TestSteps,
        LocalExecution
    ]

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        if 'export' in request.GET:
            testcase_exec = TestCaseExecution.objects.get(testcase_id=object_id)
            testcase_exec.update_library_imports(set(), request.user)
            testcase_exec.update_resource_imports(set(), request.user)
            testsuite = testcase_exec.get_testsuite(request.user)
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
            return [TestSteps]

        return self.inlines

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            form.save_m2m()
            testcase: AbstractTestCase = obj
            testcase.create_execution()
