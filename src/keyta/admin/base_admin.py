import json
from collections import defaultdict

from django.contrib import admin, messages
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.db import models
from django import forms
from django.forms import SelectMultiple, CheckboxSelectMultiple
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from tinymce.widgets import AdminTinyMCE

from keyta.widgets import ModelSelect2MultipleAdminWidget, Select2MultipleWidget # type: ignore


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
    # By default the field inlines is a tuple, which cannot be combined with a list
    inlines = []

    def add_view(self, request, form_url="", extra_context=None):
        if 'autocomplete' in request.GET:
            name = request.GET['name']
            data = self.autocomplete_name(name)

            return HttpResponse(data, content_type='application/json')

        return super().add_view(request, form_url, extra_context)

    def autocomplete_name(self, name: str):
        objects = (
            self.model.objects
            .filter(name__icontains=name)
            .values_list('name', 'systems__name')
        )
        grouped = defaultdict(list)

        for name, system in objects:
            grouped[name].append(system)

        return json.dumps([
            '%s (%s)' % (name, ', '.join(systems))
            for name, systems in grouped.items()
        ])

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if 'autocomplete' in request.GET:
            name = request.GET['name']
            data = self.autocomplete_name(name)

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

    @admin.display(description=_('Dokumentation'))
    def dokumentation(self, obj):
        return mark_safe(obj.documentation)


class BaseAddAdmin(BaseAdmin):
    fields = ['systems', 'windows', 'name']

    def get_form(self, request, obj=None, change=False, **kwargs):
        return forms.modelform_factory(
            self.model,
            fields=self.fields,
            widgets={
                'systems': ModelSelect2MultipleAdminWidget(
                    model=self.model.systems.through,
                    search_fields=['name__icontains'],
                    attrs={
                        'data-placeholder': _('System hinzufügen'),
                    }
                ),
                'windows': Select2MultipleWidget(
                    model=self.model.windows.through,
                    search_fields=['name__icontains'],
                    dependent_fields={'systems': 'systems'},
                    attrs={
                        'data-placeholder': _('Maske auswählen'),
                    }
                )
            }
        )
