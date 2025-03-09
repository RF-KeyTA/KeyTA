from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseAdmin
from keyta.admin.field_documentation import DocumentationField
from keyta.rf_import.import_resource import import_resource
from keyta.widgets import Icon, link

from ..forms import ResourceForm
from ..models import Resource
from .keywords_inline import Keywords


@admin.register(Resource)
class ResourceAdmin(DocumentationField, BaseAdmin):
    list_display = ['name', 'update']
    inlines = [Keywords]

    def get_changelist(self, request: HttpRequest, **kwargs):
        if 'update' in request.GET:
            resource = Resource.objects.get(id=int(request.GET['resource_id']))

            if error := Resource.resource_file_not_found(resource.path):
                messages.warning(request, error)
            else:
                import_resource(resource.path)
                messages.info(
                    request,
                    _(f'Die Ressource "{resource.name}" wurde erfolgreich aktualisiert')
                )

        return super().get_changelist(request, **kwargs)

    def get_fields(self, request, obj=None):
        if not obj:
            return ['path']

        return ['path'] + self.fields

    def get_form(self, request, obj=None, change=False, **kwargs):
        path_help_text = ''

        if not obj:
            path_help_text = _('Dateipfad wie beim Importieren einer Ressource in einer .robot Datei') 

        return forms.modelform_factory(
            Resource,
            fields=['path'],
            form=ResourceForm,
            labels={
                'path': 'Ressource'
            },
            help_texts={
                'path': path_help_text
            }
        )

    def get_inlines(self, request, obj):
        if not obj:
            return []

        return super().get_inlines(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return []

        return ['path'] + self.readonly_fields

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return True

    def save_form(self, request, form, change):
        resource = import_resource(form.cleaned_data['path'])
        super().save_form(request, form, change)

        return resource

    @admin.display(description=_('Aktualisierung'))
    def update(self, resource: Resource):
        return link(
            reverse('admin:resources_resource_changelist') + f'?update&resource_id={resource.id}',
            str(Icon(settings.FA_ICONS.library_update, {'font-size': '18px'}))
        )
