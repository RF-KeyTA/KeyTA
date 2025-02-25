from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext as _

from ..models import KeywordExecution
from .execution import ExecutionAdmin
from .setup_teardown_inline import SetupInline


class KeywordExecutionSetupInline(SetupInline):
    verbose_name_plural = _('Anbindung an ein laufendes System')


@admin.register(KeywordExecution)
class KeywordExecutionAdmin(ExecutionAdmin):
    inlines = [
        KeywordExecutionSetupInline
    ]

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        execution = KeywordExecution.objects.get(id=object_id)

        if not execution.test_setup():
            execution.add_attach_to_system(request.user)

        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)
