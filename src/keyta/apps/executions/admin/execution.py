import json

from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest, JsonResponse, HttpResponse

from keyta.apps.libraries.admin import LibraryImportInline
from keyta.apps.resources.admin import ResourceImportsInline
from keyta.apps.resources.models import Resource
from keyta.rf_export.rfgenerator import gen_testsuite

from ..models import Execution
from .setup_teardown_inline import SetupInline, TeardownInline


class ExecutionAdmin(admin.ModelAdmin):
    inlines = [
        SetupInline,
        TeardownInline
    ]

    def get_fields(self, request, obj=None):
        return []

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        execution: Execution = self.model.objects.get(id=object_id)

        if request.method == 'GET':
            execution.update_library_imports(request.user)
            execution.update_resource_imports()

            if 'settings' in request.GET:
                return super().change_view(request, object_id, form_url, extra_context)

            if 'to_robot' in request.GET:
                return JsonResponse(self.to_robot(execution, request.user))

        if request.method == 'PUT':
            result = json.loads(request.body.decode('utf-8'))
            execution.save_execution_result(request.user, result)
            return HttpResponse()

        return super().change_view(request, object_id, form_url, extra_context)

    def get_inlines(self, request, obj):
        execution: Execution = obj
        inlines = [LibraryImportInline]

        if execution.get_resource_dependencies():
            inlines += [ResourceImportsInline]

        return inlines + self.inlines

    def to_robot(self, execution: Execution, user: AbstractUser) -> dict:
        err = execution.validate(user)
        if err:
            return err

        testsuite = execution.get_rf_testsuite(user)
        return {
            'testsuite_name': testsuite['name'],
            'testsuite': gen_testsuite(testsuite),
            'robot_args': {
                'listener': 'keyta.Listener'
            }
        }
