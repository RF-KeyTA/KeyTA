from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext as _

from keyta.widgets import open_link_in_modal
from keyta.apps.keywords.models import Keyword

from ..models import (
    KeywordExecution,
    KeywordExecutionCall
)
from .execution_inline import ExecutionInline


class KeywordExecutionInline(ExecutionInline):
    model = KeywordExecution

    @admin.display(description=_('Werte'))
    def args(self, obj):
        execution: KeywordExecution = obj
        kw_call = KeywordExecutionCall(execution.execution_keyword_call.pk)

        if (
            execution.keyword.parameters.exists() and
            not kw_call.parameters.filter(user=self.user).exists()
        ) or kw_call.has_empty_arg(self.user):
            return open_link_in_modal(
                kw_call.get_admin_url(),
                '<i class=" error-duotone fa-solid fa-list" style="font-size: 36px;"></i>'
            )
        else:
            return open_link_in_modal(
                kw_call.get_admin_url(),
                '<i class="fa-solid fa-list" style="font-size: 36px"></i>'
            )

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
