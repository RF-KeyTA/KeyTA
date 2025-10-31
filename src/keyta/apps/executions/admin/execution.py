import json

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

        if request.method == 'GET':
            if 'log_icon' in request.GET:
                return HttpResponse(execution.get_log_icon(request.user))

            if 'result_icon' in request.GET:
                return HttpResponse(execution.get_result_icon(request.user))

            if 'settings' in request.GET:
                execution.update_imports(request.user)
                return super().change_view(request, object_id, form_url, extra_context)

        if request.method == 'POST':
            if 'to_robot' in request.GET:
                execution.update_imports(request.user)
                execution_state = json.loads(request.body.decode('utf-8'))

                if err := execution.validate(request.user, execution_state):
                    return JsonResponse(err)

                return JsonResponse(self.to_robot(request, execution, execution_state))

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

    def has_delete_permission(self, request, obj=None):
        return False

    def to_robot(self, request: HttpRequest, execution: Execution, execution_state: dict):
        get_variable_value = lambda pk: VariableValue.objects.get(pk=pk).current_value

        return execution.to_robot(get_variable_value, request.user, execution_state)
