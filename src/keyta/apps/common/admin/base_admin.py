import json

from django.contrib import admin, messages
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms import SelectMultiple, CheckboxSelectMultiple
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.utils.safestring import mark_safe

from tinymce.widgets import AdminTinyMCE # type: ignore

from apps.libraries.models import LibraryKeyword 


def autocomplete_name(name: str, app_label: str, model_name: str):
        model_class = (
            ContentType.objects.get(app_label=app_label, model=model_name)
            .model_class()
        )
        return json.dumps([
            name
            for name in
            model_class.objects.values_list('name', flat=True)
            .filter(name__icontains=name)
        ])


class BaseAdmin(admin.ModelAdmin):
    actions = None
    formfield_overrides = {
        models.TextField: {
            'widget': AdminTinyMCE
        }
    }
    list_max_show_all = 50
    list_per_page = 50
    preserve_filters = False

    def add_view(self, request, form_url="", extra_context=None):
        if 'autocomplete' in request.GET:
            app = request.GET['app']
            model = request.GET['model']
            name = request.GET['name']
            data = autocomplete_name(name, app, model)

            return HttpResponse(data, content_type='application/json')

        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if 'autocomplete' in request.GET:
            app = request.GET['app']
            model = request.GET['model']
            name = request.GET['name']
            data = autocomplete_name(name, app, model)

            return HttpResponse(data, content_type='application/json')

        return super().change_view(request, object_id, form_url, extra_context)

    def delete_view(self, request, object_id, extra_context=None):
        messages.set_level(request, messages.WARNING)

        if 'post' in request.POST and 'ref' in request.GET:
            super().delete_view(request, object_id, extra_context)
            return HttpResponseRedirect(request.GET['ref'])

        return super().delete_view(request, object_id, extra_context)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)

        if (
            hasattr(field, 'widget')
            and isinstance(field.widget, SelectMultiple)
            and field.widget.allow_multiple_selected
            and not isinstance(
                field.widget,
                (CheckboxSelectMultiple, AutocompleteSelectMultiple)
            )
        ):
            field.help_text = ''

        return field

    def save_form(self, request, form, change):
        messages.set_level(request, messages.WARNING)
        return super().save_form(request, form, change)


class BaseAdminWithDoc(BaseAdmin):
    @admin.display(description='Dokumentation')
    def read_documentation(self, obj):
        return mark_safe(obj.documentation)


class BaseReadOnlyAdmin(admin.ModelAdmin):
    list_max_show_all = 50
    list_per_page = 50
    preserve_filters = False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


class BaseDocumentationAdmin(BaseReadOnlyAdmin):
    fields = ['dokumentation']
    readonly_fields = ['dokumentation']

    def dokumentation(self, obj):
        return mark_safe(obj.documentation)

    @admin.display(description='Parameter')
    def args_table(self, obj):
        return mark_safe(obj.args_doc)

    def get_fields(self, request: HttpRequest, obj):
        keyword: LibraryKeyword = obj

        if keyword.args_doc:
            return ['args_table'] + self.fields
        
        return self.fields
    
    def get_readonly_fields(self, request: HttpRequest, obj):
        keyword: LibraryKeyword = obj

        if keyword.args_doc:
            return ['args_table'] + self.readonly_fields
        
        return self.readonly_fields
