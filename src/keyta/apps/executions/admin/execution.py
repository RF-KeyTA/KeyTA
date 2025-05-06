import json

from django.http import HttpRequest, JsonResponse, HttpResponse

from keyta.admin.base_admin import BaseAdmin
from keyta.apps.libraries.admin import LibraryImportInline
from keyta.apps.resources.admin import ResourceImportsInline

from ..models.execution import Execution, Dependencies
from .setup_teardown_inline import SetupInline, TeardownInline


class ExecutionAdmin(BaseAdmin):
    inlines = [
        SetupInline,
        TeardownInline
    ]

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        execution: Execution = self.model.objects.get(id=object_id)

        if request.method == 'GET':
            execution.update_imports(request.user)

            if 'settings' in request.GET:
                return super().change_view(request, object_id, form_url, extra_context)

            if 'to_robot' in request.GET:
                if err := execution.validate(request.user):
                    return JsonResponse(err)

                return JsonResponse(execution.to_robot(request.user))

        if request.method == 'PUT':
            result = json.loads(request.body.decode('utf-8'))
            execution.save_execution_result(request.user, result)
            return HttpResponse()

        return super().change_view(request, object_id, form_url, extra_context)

    def get_fields(self, request, obj=None):
        return []

    def get_inlines(self, request, obj):
        execution: Execution = obj
        dependencies: Dependencies = self.get_dependencies(execution)
        inlines = []

        if dependencies.libraries:
            inlines += [LibraryImportInline]

        if dependencies.resources:
            inlines += [ResourceImportsInline]

        return inlines + self.inlines

    def has_delete_permission(self, request, obj=None):
        return False
