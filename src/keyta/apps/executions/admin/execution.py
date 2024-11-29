import json

from django.contrib import admin
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.middleware.csrf import get_token

from apps.rf_export.rfgenerator import gen_testsuite
from django.contrib.auth.models import User


from .library_import_inline import LibraryImportsInline
from .resource_imports_inline import ResourceImportsInline
from .setup_teardown_inline import SetupTeardownInline
from ..models import Execution


@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    inlines = [
        LibraryImportsInline,
        ResourceImportsInline,
        SetupTeardownInline
    ]

    def get_fields(self, request, obj=None):
        return []

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        get_execution = extra_context.pop('get_execution')

        if 'settings' in request.GET:
            execution: Execution = get_execution()
            execution.update_library_imports(set(), request.user)
            execution.update_resource_imports(set(), request.user)

            return super().change_view(request, object_id, form_url, extra_context)

        if 'to_robot' in request.GET:
            execution: Execution = get_execution()
            execution.update_library_imports(set(), request.user)
            execution.update_resource_imports(set(), request.user)

            return JsonResponse({
                **self.to_robot(execution, request.user),
                'csrf_token': get_token(request)
            })

        if request.method == 'POST':
            result = json.loads(request.body.decode('utf-8'))
            get_execution().save_execution_result(request.user, result)
            return HttpResponse()

    def to_robot(self, execution: Execution, user: User) -> dict:
        err = execution.validate(user)
        if err:
            return err

        testsuite = execution.get_testsuite(user)
        return {
            'testsuite_name': testsuite['name'],
            'testsuite': gen_testsuite(testsuite),
            'robot_args': {
                'listener': 'keyta.Listener'
            }
        }
