from django import forms
from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseAdmin

from ..models import ResourceImport


# This admin is necessary in order to delete ResourceImports
@admin.register(ResourceImport)
class ResourceImportAdmin(BaseAdmin):
    form = forms.modelform_factory(
        ResourceImport,
        fields=['window'],
        labels = {
            'window': _('Maske')
        }
    )

    def get_fields(self, request, obj=None):
        return self.get_readonly_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        resource_import: ResourceImport = obj

        if resource_import.window:
            return ['window']
        
        return []
