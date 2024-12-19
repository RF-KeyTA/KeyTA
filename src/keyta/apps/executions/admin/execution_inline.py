from django.contrib import admin
from django.http import HttpRequest
from django.urls import get_script_prefix
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from apps.common.widgets import open_link_in_modal, link
from apps.executions.models import Execution


class ExecutionInline(admin.TabularInline):
    model = Execution
    extra = 0
    max_num = 1
    can_delete = False
    template = 'admin/execution/tabular.html'

    @admin.display(description=_('Einstellungen'))
    def settings(self, obj: Execution):
        return open_link_in_modal(
            obj.get_admin_url() + '?settings',
            '<i class=" fa-solid fa-gear" style="font-size: 36px"></i>'
        )

    def get_fields(self, request, obj=None):
        return ['settings', 'start', 'result_icon', 'log_icon']

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        self.user = request.user
        return ['settings', 'start', 'result_icon', 'log_icon']

    @admin.display(description=_('Protokoll'))
    def log_icon(self, obj):
        exec: Execution = obj
        user_exec = exec.user_execs.get(user=self.user)

        if user_exec.result and not user_exec.running:
            return link(
                get_script_prefix() + user_exec.log,
                '<i class="fa-regular fa-file-lines" style="font-size: 36px"></i>',
                True
            )

        return '-'

    @admin.display(description=_('Ergebnis'))
    def result_icon(self, obj):
        exec: Execution = obj
        user_exec = exec.user_execs.get(user=self.user)

        if (result := user_exec.result) and not user_exec.running:
            if result == 'FAIL':
                return mark_safe('<img src="/static/img/Fail.png" width="35">')

            if result == 'PASS':
                return mark_safe('<img src="/static/img/Pass.png" width="35">')

        return '-'

    @admin.display(description=_('Ausf.'))
    def start(self, obj):
        url = obj.get_admin_url() + '?start'
        title = '<i class=" fa-solid fa-circle-play" style="font-size: 36px"></i>'
        return mark_safe('<a href="%s" id="exec-btn">%s</a>' % (url, title))
