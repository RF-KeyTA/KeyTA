from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from apps.windows.models import WindowKeywordReturnValue


@admin.register(WindowKeywordReturnValue)
class WindowKeywordReturnValueAdmin(BaseAdmin):
    pass
