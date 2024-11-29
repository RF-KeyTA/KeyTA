from django.contrib import admin

from apps.common.admin import BaseAdmin
from ..models import LibraryImport


@admin.register(LibraryImport)
class LibraryImportAdmin(BaseAdmin):
    pass
