from django.contrib import admin

from apps.common.admin.base_admin import BaseAdmin
from apps.windows.models import WindowKeywordParameter


@admin.register(WindowKeywordParameter)
class WindowKeywordParameterAdmin(BaseAdmin):
    pass
