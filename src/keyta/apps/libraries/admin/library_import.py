from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models import LibraryImport


@admin.register(LibraryImport)
class LibraryImportAdmin(BaseAdmin):
    pass
