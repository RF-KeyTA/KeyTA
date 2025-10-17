from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe

from keyta.apps.executions.models import TestCaseExecution
from keyta.rf_export.rfgenerator import gen_testsuite

from ..models import TestCase
from .base_testcase_admin import BaseTestCaseAdmin


@admin.register(TestCase)
class TestCaseAdmin(BaseTestCaseAdmin):
    change_form_template = 'testcase_change_form.html'

    def get_list_display(self, request):
        return ['empty'] + super().get_list_display(request)

    @admin.display(description='')
    def empty(self, obj):
        return mark_safe('&nbsp;')

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        if 'export' in request.GET:
            execution = TestCaseExecution.objects.get(testcase_id=object_id)

            if err := execution.validate(request.user):
                messages.warning(request, err['error'])
                return HttpResponseRedirect(request.path)
            else:
                execution.update_imports(request.user)
                testsuite = execution.get_rf_testsuite(request.user)
                robot_file = testsuite['name'] + '.robot'

                return HttpResponse(
                    gen_testsuite(testsuite),
                    headers={
                        'Content-Type': 'text/plain',
                        'Content-Disposition': f'attachment; filename="{robot_file}"'
                    }
                )

        current_app, model, *route = request.resolver_match.route.split('/')
        app = settings.MODEL_TO_APP.get(model)

        if app and app != current_app:
            return HttpResponseRedirect(reverse('admin:%s_%s_change' % (app, model), args=(object_id,)))

        return super().change_view(request, object_id, form_url, extra_context)
