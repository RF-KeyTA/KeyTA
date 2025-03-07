from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseAdmin

from ..models import ResourceImport


# This admin is necessary in order to delete ResourceImports
@admin.register(ResourceImport)
class ResourceImportAdmin(BaseAdmin):
    pass
