from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models import Q
from django.forms import ModelMultipleChoiceField
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_admin import (
    BaseAdmin,
    BaseDocumentationAdmin,
    BaseQuickAddAdmin
)
from keyta.admin.field_documentation import DocumentationField
from keyta.admin.list_filters import SystemListFilter
from keyta.apps.resources.models import Resource
from keyta.apps.variables.models import Variable
from keyta.forms.baseform import form_with_select
from keyta.widgets import CheckboxSelectMultipleSystems, Icon, open_link_in_modal

from ..forms import TemplateVariablesFormset, WindowForm
from ..models import (
    Window,
    WindowDocumentation,
    WindowQuickAdd,
    WindowQuickChange
)
from .actions_inline import Actions
from .resources_inline import Resources
from .sequences_inline import Sequences
from .variables_inline import Variables


@admin.register(Window)
class WindowAdmin(DocumentationField, BaseAdmin):
    list_display = ['name', 'preview', 'system_list']
    list_display_links = ['name']
    list_filter = [
        ('systems', SystemListFilter),
    ]
    list_per_page = 10
    search_fields = ['name']
    search_help_text = _('Name')

    @admin.display(description=_('Vorschau'))
    def preview(self, window: Window):
        return open_link_in_modal(
            WindowDocumentation.objects.get(id=window.pk).get_admin_url(),
            str(Icon(settings.FA_ICONS.preview, {'font-size': '18px'}))
        )

    @admin.display(description=_('Systeme'))
    def system_list(self, window: Window):
        return ', '.join(
            window.systems.values_list('name', flat=True)
        )

    fields = ['systems', 'name', 'description']
    form = form_with_select(
        Window,
        'systems',
        _('System hinzufügen'),
        form_class=WindowForm,
        select_many=True
    )
    inlines = [
        Actions,
        Sequences,
        Variables
    ]

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        if 'quick_change' in request.GET:
            window = WindowQuickChange.objects.get(pk=object_id)
            return HttpResponseRedirect(window.get_admin_url() + '?_popup=1')

        if 'view' in request.GET:
            window_doc = WindowDocumentation.objects.get(id=object_id)
            return HttpResponseRedirect(window_doc.get_admin_url())

        return super().change_view(request, object_id, form_url, extra_context)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'systems':
            field = ModelMultipleChoiceField(
                widget=CheckboxSelectMultipleSystems,
                queryset=field.queryset
            )
            field.label = _('Systeme')

            if window_id := request.resolver_match.kwargs.get('object_id'):
                window = Window.objects.get(id=window_id)
                field.widget.in_use = set(window.keywords.values_list('systems', flat=True))

        return field

    def get_inlines(self, request, obj):
        if not obj:
            return []

        if Resource.objects.count():
            return [Resources] + self.inlines

        return self.inlines

    def get_protected_objects(self, obj):
        window: Window = obj
        return list(window.actions.all()) + list(window.sequences.all()) + list(window.variables.all())

    def has_add_permission(self, request):
        return self.can_add(request.user, 'window')

    def has_change_permission(self, request, obj=None):
        return self.can_change(request.user, 'window')

    def has_delete_permission(self, request, obj=None):
        return self.can_delete(request.user, 'window')


@admin.register(WindowDocumentation)
class WindowDocumentationAdmin(BaseDocumentationAdmin):
    fields = []


@admin.register(WindowQuickAdd)
class WindowQuickAddAdmin(BaseQuickAddAdmin):
    fields = ['systems', 'name']
    form = WindowForm

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'systems':
            field.widget = forms.MultipleHiddenInput()

        return field


class WindowVariables(Variables):
    readonly_fields = []

    def has_change_permission(self, request, obj=None):
        return True


class TemplateVariables(Variables):
    formset = TemplateVariablesFormset
    verbose_name = _('Dynamisches Wert')
    verbose_name_plural = _('Dynamische Werte')

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(variable__template='')

    def has_change_permission(self, request, obj=None):
        return True


@admin.register(WindowQuickChange)
class WindowQuickChangeAdmin(WindowAdmin):
    fields = []
    readonly_fields = ['documentation']

    def get_inlines(self, request, obj):
        if Variable.objects.filter(~Q(template='')).exists():
            inlines = [WindowVariables, TemplateVariables]
        else:
            inlines = [WindowVariables]

        if Resource.objects.count():
            return [Resources] + inlines

        return inlines

    def has_delete_permission(self, request, obj=None):
        return False
