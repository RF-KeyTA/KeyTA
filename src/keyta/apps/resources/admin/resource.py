import tempfile
from pathlib import Path

from django import forms
from django.contrib import admin
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from apps.common.admin import BaseAdmin
from apps.resources.models import Resource, ResourceKeyword
from apps.rf_import.import_resource import import_resource


class Keywords(admin.TabularInline):
    model = ResourceKeyword
    fields = ['name', 'short_doc']
    readonly_fields = ['name', 'short_doc']
    extra = 0
    can_delete = False
    show_change_link = True
    verbose_name_plural = _('Schlüsselwörter')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Resource)
class ResourceAdmin(BaseAdmin):
    list_display = ['name']
    ordering = ['name']
    inlines = [Keywords]

    def dokumentation(self, obj):
        return mark_safe(obj.documentation)

    def get_fields(self, request, obj=None):
        if not obj:
            return ['name']

        return ['dokumentation']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'name':
            return forms.FileField()

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return []

        return ['dokumentation']

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
