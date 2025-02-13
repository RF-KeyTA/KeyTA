from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext as _

from keyta.apps.keywords.models import Keyword
from keyta.apps.keywords.admin import KeywordCallArgsField

from ..models import KeywordExecution
from .execution_inline import ExecutionInline


class KeywordExecutionInline(KeywordCallArgsField, ExecutionInline):
    model = KeywordExecution

    @admin.display(description=_('Werte'))
    def args(self, execution: KeywordExecution ):
        return super().args(execution.execution_keyword_call)

    def get_fields(self, request, obj=None):
        keyword: Keyword = obj

        if keyword.parameters.exists():
            return ['args'] + super().get_fields(request, obj)
        else:
            return super().get_fields(request, obj)

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        self.user = request.user
        keyword: Keyword = obj

        if keyword.parameters.exists():
            return ['args'] + super().get_readonly_fields(request, obj)
        else:
            return super().get_readonly_fields(request, obj)
