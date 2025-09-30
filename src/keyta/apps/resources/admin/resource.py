from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_admin import BaseAdmin
from keyta.admin.field_documentation import DocumentationField
from keyta.admin.keywords_inline import Keywords
from keyta.apps.keywords.models import KeywordCall
from keyta.rf_import.import_resource import import_resource
from keyta.widgets import Icon, link

from ..forms import ResourceForm
from ..models import Resource


@admin.register(Resource)
class ResourceAdmin(DocumentationField, BaseAdmin):
    list_display = ['name', 'update']
    form = ResourceForm
    fields = ['path']
    readonly_fields = ['documentation']
    inlines = [Keywords]

    @admin.display(description=_('Aktualisierung'))
    def update(self, resource: Resource):
        return link(
            reverse('admin:resources_resource_changelist') + f'?update&resource_id={resource.id}',
            str(Icon(settings.FA_ICONS.library_update, {'font-size': '18px'}))
        )

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

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'path':
            field.label = _('Ressource')
            field.help_text = _('Dateipfad wie beim Importieren einer Ressource in einer .robot Datei')

        return field

    def get_fields(self, request, obj=None):
        if not obj:
            return ['path']

        return super().get_fields(request, obj)

    def get_inlines(self, request, obj):
        if not obj:
            return []

        return super().get_inlines(request, obj)

    def get_protected_objects(self, obj: Resource):
        return KeywordCall.objects.filter(to_keyword__resource=obj)

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return []

        return super().get_readonly_fields(request, obj)

    def save_form(self, request, form, change):
        if change:
            return super().save_form(request, form, change)
        else:
            resource = import_resource(form.cleaned_data['path'])
            super().save_form(request, form, change)
            return resource
