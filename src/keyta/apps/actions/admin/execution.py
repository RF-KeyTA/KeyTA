from django.contrib import admin
from django.http import HttpRequest

from apps.executions.admin import KeywordExecutionAdmin
from ..models import ActionExecution


@admin.register(ActionExecution)
class ActionExecutionAdmin(KeywordExecutionAdmin):
    def change_view(self, request: HttpRequest, object_id, form_url="",
                    extra_context=None):
        context = {
            'get_execution': lambda: ActionExecution.objects.get(id=object_id)
        }

        return super().change_view(request, object_id, form_url, context)
