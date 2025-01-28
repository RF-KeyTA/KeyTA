from django.contrib import admin
from django.db.models import QuerySet

from keyta.admin.base_admin import BaseAdmin

from apps.keywords.admin import KeywordCallParametersInline
from apps.keywords.forms import KeywordCallParameterFormset
from apps.keywords.models import KeywordCall

from ..models.keyword_execution_call import KeywordExecutionCall


class KeywordExecutionCallParameterFormset(KeywordCallParameterFormset):
    def get_choices(self, obj):
        kw_call: KeywordCall = obj
        keyword = kw_call.execution.keyword
        window_ids = list(keyword.windows.values_list('id', flat=True))
        system_ids = list(keyword.systems.values_list('id', flat=True))

        return self.get_variables(
            window_ids,
            system_ids,
            lambda value_ref: str(value_ref)
        )


class KeywordCallParameters(KeywordCallParametersInline):
    formset = KeywordExecutionCallParameterFormset

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        return queryset.filter(user=request.user)


@admin.register(KeywordExecutionCall)
class KeywordExecutionCallAdmin(BaseAdmin):
    inlines = [KeywordCallParameters]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        kw_call = KeywordExecutionCall.objects.get(id=object_id)

        for param in kw_call.to_keyword.parameters.all():
            kw_call.add_parameter(param, user=request.user)

        return super().change_view(request, object_id, form_url, extra_context)

    def get_fields(self, request, obj=None):
        return []
