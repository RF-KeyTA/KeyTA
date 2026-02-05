from django.http import HttpRequest

from keyta.apps.keywords.admin.field_keywordcall_values import KeywordCallValuesField
from keyta.apps.keywords.models import Keyword

from ..models import KeywordExecution
from .execution_inline import ExecutionInline


class ExecutionKeywordCallValuesField(KeywordCallValuesField):
    def get_user(self, request):
        return request.user

    def get_kw_call(self, obj):
        kw_execution: KeywordExecution = obj
        return kw_execution.execution_keyword_call

    def get_fields(self, request: HttpRequest, obj=None):
        keyword: Keyword = obj

        fields = [
            field
            for field in super().get_fields(request, obj)
            if field != self.name
        ]

        if keyword.parameters.exists():
            return [self.name] + fields

        return fields


class KeywordExecutionInline(ExecutionKeywordCallValuesField, ExecutionInline):
    model = KeywordExecution
