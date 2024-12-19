from django.contrib import admin
from django.utils.translation import gettext as _

from apps.executions.models import (
    Execution,
    KeywordExecutionCall,
    ExecutionLibraryImport
)
from apps.keywords.admin import KeywordAdmin
from apps.libraries.models import Library
from apps.windows.models import WindowKeyword, Window


class WindowKeywordAdmin(KeywordAdmin):
    list_display = ['system_list', 'name', 'short_doc']
    list_filter = ['systems']

    @admin.display(description=_('Systeme'))
    def system_list(self, obj: Window):
        return list(obj.systems.values_list('name', flat=True))

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
