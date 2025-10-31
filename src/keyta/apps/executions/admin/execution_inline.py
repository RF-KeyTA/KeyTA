from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.widgets import open_link_in_modal, Icon

from ..models import Execution


class ExecutionInline(BaseTabularInline):
    model = Execution
    extra = 0
    max_num = 1
    can_delete = False
    template = 'execution_inline_tabular.html'

    def get_fields(self, request, obj=None):
        return self.get_readonly_fields(request, obj)

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        @admin.display(description=_('Ergebnis'))
        def result_icon(self, execution: Execution):
            return mark_safe(execution.get_result_icon(request.user))

        @admin.display(description=_('Protokoll'))
        def log_icon(self, execution: Execution):
            return mark_safe(execution.get_log_icon(request.user))

        ExecutionInline.result_icon = result_icon
        ExecutionInline.log_icon = log_icon

        return ['settings', 'start', 'result_icon', 'log_icon']

    @admin.display(description=_('Einstellungen'))
    def settings(self, execution: Execution):
        return open_link_in_modal(
            execution.get_admin_url() + '?settings',
            str(Icon(settings.FA_ICONS.exec_settings))
        )

    @admin.display(description=_('Ausführung'))
    def start(self, execution: Execution):
        url = execution.get_admin_url() + '?start'
        title = str(Icon(settings.FA_ICONS.exec_start))

        return mark_safe('<a href="%s" id="exec-btn">%s</a>' % (url, title))
