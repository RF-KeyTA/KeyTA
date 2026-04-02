import json

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

from keyta.admin.base_admin import BaseAdmin
from keyta.apps.libraries.admin import LibraryImportInline
from keyta.apps.resources.admin import ResourceImportsInline

from ..models import Execution, UserExecution
from .setup_teardown_inline import SetupInline, TeardownInline


class ExecutionAdmin(BaseAdmin):
    inlines = [
        SetupInline,
        TeardownInline
    ]

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        execution: Execution = self.model.objects.get(id=object_id)
        user_exec, _ = UserExecution.objects.get_or_create(
            execution=execution,
            user=request.user
        )

        if 'log_icon' in request.GET:
            return HttpResponse(execution.get_log_icon(settings.RF_SERVER, request.user))

        if 'result_icon' in request.GET:
            return HttpResponse(execution.get_result_icon(request.user))

        if 'settings' in request.GET:
            execution.update_imports(request.user)
            return super().change_view(request, object_id, form_url, extra_context)

        if 'to_robot' in request.GET:
            execution_state = json.loads(request.body.decode('utf-8'))
            return JsonResponse(execution.export_to_robot(request.user, execution_state))

        if request.method == 'PUT':
            result = json.loads(request.body.decode('utf-8'))
            execution.save_execution_result(request.user, result['log'], result['result'])
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
