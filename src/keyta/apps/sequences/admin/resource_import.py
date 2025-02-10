from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models import SequenceResourceImport


@admin.register(SequenceResourceImport)
class SequenceResourceImportAdmin(BaseAdmin):
    pass
