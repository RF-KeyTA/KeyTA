from django.contrib import admin

from keyta.apps.keywords.admin import KeywordCallAdmin, KeywordCallParametersInline
from keyta.apps.keywords.models import ExecutionKeywordCall

from ..forms import KeywordCallExecutionParameterFormset


class KeywordCallParameters(KeywordCallParametersInline):
    formset = KeywordCallExecutionParameterFormset

    def get_queryset(self, request):
        return super().get_queryset(request).filter(user=request.user)


@admin.register(ExecutionKeywordCall)
class KeywordCallExecutionAdmin(KeywordCallAdmin):
    readonly_fields = []
    inlines = [KeywordCallParameters]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        kw_call = ExecutionKeywordCall.objects.get(id=object_id)
        kw_call.update_parameters(request.user)
        return super().change_view(request, object_id, form_url, extra_context)

    def get_fields(self, request, obj=None):
        return []
