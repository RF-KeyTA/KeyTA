import json

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
    ordering = ['name']
    form = forms.modelform_factory(
        Resource,
        fields=['name'],
        form=ResourceForm,
        labels={
            'name': _('Filename (ending with .resource)')
        }
    )
    inlines = [Keywords]

    def autocomplete_name(self, name: str, request: HttpRequest):
        return json.dumps([
            name + '.resource'
            for name in
            self.model.objects.values_list('name', flat=True)
            .filter(name__icontains=name.rstrip('.resource'))
        ])

    def get_changelist(self, request: HttpRequest, **kwargs):
        if 'update' in request.GET:
            resource = Resource.objects.get(id=int(request.GET['resource_id']))

            if error := Resource.resource_file_not_found(resource.name + '.resource'):
                messages.warning(request, error)
            else:
                import_resource(resource.name + '.resource')
                messages.info(
                    request,
                    _(f'Die Ressource "{resource.name}" wurde erfolgreich aktualisiert')
                )

        return super().get_changelist(request, **kwargs)

    def get_fields(self, request, obj=None):
        if not obj:
            return ['name']

        return self.fields

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
        resource_name = form.cleaned_data.get('name', None)
        resource = import_resource(str(resource_name))
        
        super().save_form(request, form, change)

        return resource

    @admin.display(description=_('Aktualisierung'))
    def update(self, resource: Resource):
        return link(
            reverse('admin:resources_resource_changelist') + f'?update&resource_id={resource.id}',
            str(Icon(settings.FA_ICONS.library_update, {'font-size': '18px'}))
        )
