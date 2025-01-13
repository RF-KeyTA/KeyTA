import json
from django.contrib import admin
from django.utils.translation import gettext as _

from apps.executions.models import (
    Execution,
    KeywordExecutionCall
)
from apps.keywords.admin import KeywordAdmin
from apps.windows.models import WindowKeyword, Window


class WindowKeywordAdminMixin:
    def autocomplete_name(self, name: str):
        return json.dumps([
            '%s (%s -> %s)' % (name, systems, windows or _('Systemweit'))
            for name, systems, windows in
            self.model.objects.values_list('name', 'systems__name', 'windows__name')
            .filter(name__icontains=name)
        ])

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        keyword: WindowKeyword = obj

        if not change:
            form.save_m2m()

            execution = Execution.objects.create(keyword=keyword)
            KeywordExecutionCall.objects.create(
                execution=execution,
                to_keyword=keyword,
            )


class WindowKeywordAdmin(WindowKeywordAdminMixin, KeywordAdmin):
    list_display = ['system_list', 'name', 'short_doc']
    list_filter = ['systems']

    @admin.display(description=_('Systeme'))
    def system_list(self, obj: Window):
        return list(obj.systems.values_list('name', flat=True))

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return super().changeform_view(request, object_id, form_url, extra_context)
