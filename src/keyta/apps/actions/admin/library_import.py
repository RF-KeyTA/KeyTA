from django.contrib import admin

from apps.common.admin.base_admin import BaseAdmin

from ..models.library_import import ActionLibraryImport


@admin.register(ActionLibraryImport)
class ActionLibraryImportAdmin(BaseAdmin):
    pass
