import json

from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest, JsonResponse, HttpResponse

from keyta.admin.base_admin import BaseAdmin
from keyta.apps.libraries.admin import LibraryImportInline
from keyta.apps.resources.admin import ResourceImportsInline
from keyta.apps.variables.models import VariableValue

from ..models.execution import Execution
from .setup_teardown_inline import SetupInline, TeardownInline


class ExecutionAdmin(BaseAdmin):
    inlines = [
        SetupInline,
        TeardownInline
    ]

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        execution: Execution = self.model.objects.get(id=object_id)

        if 'log_icon' in request.GET:
            return HttpResponse(execution.get_log_icon(request.user))

        if 'result_icon' in request.GET:
            return HttpResponse(execution.get_result_icon(request.user))

        if 'settings' in request.GET:
            execution.update_imports(request.user)
            return super().change_view(request, object_id, form_url, extra_context)

        if 'to_robot' in request.GET:
            return self.handle_to_robot(request, execution)

        if request.method == 'PUT':
            result = json.loads(request.body.decode('utf-8'))
            execution.save_execution_result(request.user, result)
            return HttpResponse()

        return super().change_view(request, object_id, form_url, extra_context)

    def get_fields(self, request, obj=None):
        return []

    def get_inlines(self, request, obj):
        execution: Execution = obj
        dependencies = execution.get_keyword_dependencies()
        inlines = []

        if dependencies.libraries:
            inlines += [LibraryImportInline]

        if dependencies.resources:
            inlines += [ResourceImportsInline]

        return inlines + self.inlines

    def export_to_robot(self, execution: Execution, user: AbstractUser, execution_state: dict) -> dict:
        if err := execution.validate(user, execution_state):
            return err

        execution.update_imports(user)
        get_variable_value = lambda pk: VariableValue.objects.get(pk=pk).current_value
        testsuite = execution.get_rf_testsuite(get_variable_value, user, execution_state, include_doc=False)

        return execution.to_robot(testsuite)

    def handle_to_robot(self, request: HttpRequest, execution: Execution) -> HttpResponse:
        execution_state = json.loads(request.body.decode('utf-8'))
        return JsonResponse(self.export_to_robot(execution, request.user, execution_state))

    def has_delete_permission(self, request, obj=None):
        return False
