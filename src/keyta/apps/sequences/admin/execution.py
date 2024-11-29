from django.contrib import admin
from django.http import HttpRequest

from apps.executions.admin import (
    KeywordExecutionAdmin,  
    KeywordExecutionSetupInline, 
    LibraryImportsInline, 
    ResourceImportsInline
)
from ..models import SequenceExecution


@admin.register(SequenceExecution)
class SequenceExecutionAdmin(KeywordExecutionAdmin):
    inlines = [
        LibraryImportsInline,
        ResourceImportsInline,
        KeywordExecutionSetupInline
    ]


    def change_view(self, request: HttpRequest, object_id, form_url="",
                    extra_context=None):
        context = {
            'get_execution': lambda: SequenceExecution.objects.get(id=object_id)
        }

        return super().change_view(request, object_id, form_url, context)
