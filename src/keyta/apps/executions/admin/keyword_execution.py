from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext as _

from keyta.apps.executions.admin.execution import ExecutionAdmin
from keyta.apps.libraries.admin import LibraryImportInline

from ..models import KeywordExecution
from .setup_teardown_inline import SetupInline


class KeywordExecutionSetupInline(SetupInline):
    verbose_name_plural = _('Anbindung an ein laufendes System')

    def get_fields(self, request, obj=None):
        return ['enabled'] + super().get_fields(request, obj)


@admin.register(KeywordExecution)
class KeywordExecutionAdmin(ExecutionAdmin):
    inlines = [
        LibraryImportInline,
        KeywordExecutionSetupInline
    ]

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        execution = KeywordExecution.objects.get(id=object_id)
        execution.add_attach_to_system(request.user)
        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)
