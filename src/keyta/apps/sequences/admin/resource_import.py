from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models.resource_import import SequenceResourceImport


@admin.register(SequenceResourceImport)
class SequenceResourceImportAdmin(BaseAdmin):
    pass
