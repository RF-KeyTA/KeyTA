from django.contrib import admin

from apps.common.admin import BaseAdmin
from apps.windows.models import WindowKeywordReturnValue


@admin.register(WindowKeywordReturnValue)
class WindowKeywordReturnValueAdmin(BaseAdmin):
    pass
