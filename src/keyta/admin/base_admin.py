import json
from collections import defaultdict

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.forms import SelectMultiple, CheckboxSelectMultiple
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


from keyta.widgets import BaseSelectMultiple, quick_add_widget

from .field_documentation import DocumentationField


class ListView(ChangeList):
    def __init__(
        self,
        request,
        model,
        list_display,
        list_display_links,
        list_filter,
        date_hierarchy,
        search_fields,
        list_select_related,
        list_per_page,
        list_max_show_all,
        list_editable,
        model_admin,
        sortable_by,
        search_help_text,
    ):
        super().__init__(request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields, list_select_related, list_per_page, list_max_show_all, list_editable, model_admin, sortable_by, search_help_text)

        self.title = model._meta.verbose_name_plural


class BaseAdmin(admin.ModelAdmin):
    actions = [] if settings.DEBUG else None
    list_max_show_all = 50
    list_per_page = 50
    preserve_filters = False
    # By default, inlines and readonly_fields are tuples, which cannot be combined with a list
    inlines = []
    readonly_fields = []
    sortable_by = []

    def add_view(self, request: HttpRequest, form_url="", extra_context=None):
        if 'autocomplete' in request.GET:
            name = str(request.GET['name'])
            data = self.autocomplete_name(name, request)

            return HttpResponse(data, content_type='application/json')

        return super().add_view(request, form_url, extra_context)

    def autocomplete_name_queryset(self, name: str, request: HttpRequest):
        return self.model.objects.filter(name__icontains=name)

    def autocomplete_name(self, name: str, request: HttpRequest) -> str:
        grouped = defaultdict(list)
        name_system = (
            self.autocomplete_name_queryset(name, request)
            .values_list('name', 'systems__name')
        )

        for key, value in name_system:
            grouped[key].append(value)

        return json.dumps([
            '%s (%s)' % (group, ', '.join(items))
            for group, items in grouped.items()
        ])

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if 'autocomplete' in request.GET:
            name = request.GET['name']
            data = self.autocomplete_name(name, request)

            return HttpResponse(data, content_type='application/json')

        return super().change_view(request, object_id, form_url, extra_context)

    def delete_view(self, request, object_id, extra_context=None):
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

    def get_changelist(self, request, **kwargs):
        return ListView

    def get_deleted_objects(self, objs, request):
        deleted_objects, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)

        protected = [
            mark_safe('%s: <a href="%s" target="_blank">%s</a>' % (obj._meta.verbose_name, obj.get_admin_url(), str(obj)))
            for obj in self.get_protected_objects(objs[0])
        ]

        # The action 'Delete selected elements' was executed
        if 'action' in request.POST:
            to_be_deleted = [
                mark_safe(
                    '%s: <a href="%s" target="_blank">%s</a>' % (obj._meta.verbose_name, obj.get_admin_url(), str(obj)))
                for obj in objs
            ]
        # Trying to delete a single element
        else:
            to_be_deleted = [
                mark_safe('%s: <a href="%s" target="_blank">%s</a>' % (obj._meta.verbose_name, obj.get_admin_url(), str(obj)))
                for obj in self.get_related_objects(objs[0])
            ]

        return to_be_deleted, model_count, perms_needed, protected

    def get_protected_objects(self, obj):
        return []

    def get_related_objects(self, obj):
        return []

    def save_form(self, request, form, change):
        messages.set_level(request, messages.WARNING)
        return super().save_form(request, form, change)


class BaseReadOnlyAdmin(admin.ModelAdmin):
    list_max_show_all = 50
    list_per_page = 50
    preserve_filters = False
    # By default, readonly_fields is a tuple, which cannot be combined with a list
    readonly_fields = []

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


class BaseDocumentationAdmin(DocumentationField, BaseReadOnlyAdmin):
    fields = []


class BaseQuickAddAdmin(BaseAdmin):
    fields = ['systems', 'windows', 'name']

    def add_view(self, request, form_url='', extra_context=None):
        if request.POST and 'ref' in request.GET:
            response = super().add_view(request, form_url, extra_context)

            if hasattr(response, 'context_data') and response.context_data.get('errors'):
                return response
            else:
                response = """
                <script>
                (function() {
                    window.parent.dismissRelatedObjectModal()
                    new Promise(r => setTimeout(r, 500));
                    window.parent.location.reload()
                })();
                </script>
                """
                return HttpResponse(response)

        return super().add_view(request, form_url, extra_context)

    def autocomplete_name_queryset(self, name: str, request: HttpRequest):
        queryset = super().autocomplete_name_queryset(name, request)

        if 'windows' in request.GET:
            queryset = queryset.filter(windows__in=[request.GET['windows']])

        return queryset

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'systems':
            field.widget = BaseSelectMultiple(_('System auswählen'))

        if db_field.name == 'windows':
            field.widget = forms.MultipleHiddenInput()

        return field


class QuickAddMixin:
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == self.quick_add_field:
            app = self.quick_add_model._meta.app_label
            model = self.quick_add_model._meta.model_name
            quick_add_url = reverse('admin:%s_%s_add' % (app, model))

            field.widget = quick_add_widget(
                field.widget,
                quick_add_url,
                self.quick_add_url_params(request, {})
            )

        return field

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def quick_add_url_params(self, request: HttpRequest, url_params: dict):
        return {}
