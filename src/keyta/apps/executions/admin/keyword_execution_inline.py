from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext as _

from keyta.apps.keywords.admin.field_keywordcall_args import BaseKeywordCallArgs
from keyta.apps.keywords.models import Keyword, ExecutionKeywordCall

from ..models import KeywordExecution
from .execution_inline import ExecutionInline


class KeywordCallArgsField(BaseKeywordCallArgs):
    def get_fields(self, request, obj=None):
        return self.get_readonly_fields(request, obj)

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        @admin.display(description=_('Werte'))
        def args(self, execution: KeywordExecution):
            execution_kw_call = ExecutionKeywordCall.objects.get(
                pk=execution.execution_keyword_call.pk
            )
            return super().get_icon(execution_kw_call, request.user)

        keyword: Keyword = obj
        if keyword.parameters.exists():
            KeywordCallArgsField.args = args
            return ['args'] + super().get_readonly_fields(request, obj)
        
        return super().get_readonly_fields(request, obj)


class KeywordExecutionInline(KeywordCallArgsField, ExecutionInline):
    model = KeywordExecution
