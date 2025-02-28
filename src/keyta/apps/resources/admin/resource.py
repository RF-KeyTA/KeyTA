import tempfile
from pathlib import Path

from django import forms
from django.contrib import admin
from django.http import HttpRequest

from keyta.admin.base_admin import BaseAdmin
from keyta.admin.field_documentation import DocumentationField
from keyta.rf_import.import_resource import import_resource

from ..models import Resource
from .keywords_inline import Keywords


@admin.register(Resource)
class ResourceAdmin(DocumentationField, BaseAdmin):
    list_display = ['name']
    ordering = ['name']
    inlines = [Keywords]

    def get_fields(self, request, obj=None):
        if not obj:
            return ['name']

        return self.fields

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'name':
            return forms.FileField()

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return []

        return self.readonly_fields

    def get_inlines(self, request, obj):
        if not obj:
            return []

        return super().get_inlines(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def save_form(self, request, form, change):
        file_obj = request.FILES['name']
        file_name = str(file_obj._name)
        tmp_resource = Path(tempfile.gettempdir()) / file_name

        with open(tmp_resource, 'w', encoding='utf-8') as fp:
            fp.write(file_obj.file.read().decode())

        resource = import_resource(str(tmp_resource))
        super().save_form(request, form, change)

        return resource
