import json
from collections import defaultdict

from django.contrib import admin
from django.utils.translation import gettext as _

from apps.windows.models import Window

from ..models import WindowKeyword
from .keyword import KeywordAdmin


class WindowKeywordAdminMixin:
    def autocomplete_name(self, name: str):
        keywords = (
            self.model.objects
            .filter(name__icontains=name)
            .values_list('name', 'systems__name')
        )
        grouped_keywords = defaultdict(list)

        for name, system in keywords:
            grouped_keywords[name].append(system)

        return json.dumps([
            '%s (%s)' % (name, ', '.join(systems))
            for name, systems in grouped_keywords.items()
        ])

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        keyword: WindowKeyword = obj

        if not change:
            form.save_m2m()
            keyword.create_execution()


class WindowKeywordAdmin(WindowKeywordAdminMixin, KeywordAdmin):
    list_display = ['system_list', 'name', 'short_doc']
    list_filter = ['systems']

    @admin.display(description=_('Systeme'))
    def system_list(self, obj: Window):
        return list(obj.systems.values_list('name', flat=True))

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return super().changeform_view(request, object_id, form_url, extra_context)
