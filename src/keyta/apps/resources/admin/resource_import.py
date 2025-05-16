from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_admin import BaseAdmin
from keyta.models.base_model import AbstractBaseModel
from keyta.widgets import link

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
        
        if execution := resource_import.execution:
            if execution.keyword:
                return ['from_sequence']

            if execution.testcase:
                return ['from_testcase']
        
        return []

    @admin.display(description=_('Sequenz'))
    def from_sequence(self, obj):
        resource_import: ResourceImport = obj
        execution = resource_import.execution
        entity: AbstractBaseModel = execution.keyword

        return link(entity.get_admin_url(), str(entity))

    @admin.display(description=_(message='Testfall'))
    def from_testcase(self, obj):
        resource_import: ResourceImport = obj
        execution = resource_import.execution
        entity: AbstractBaseModel = execution.testcase

        return link(entity.get_admin_url(), str(entity))
