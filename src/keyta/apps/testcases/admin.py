from django.contrib import admin
from django.http import HttpRequest, HttpResponse

from keyta.admin.testcase import BaseTestCaseAdmin
from keyta.apps.executions.models import TestCaseExecution
from keyta.rf_export.rfgenerator import gen_testsuite

from .models import TestCase


@admin.register(TestCase)
class TestCaseAdmin(BaseTestCaseAdmin):
    change_form_template = 'change_form.html'

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
