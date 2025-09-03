from django import forms
from django.contrib import admin
from django.forms import ModelMultipleChoiceField
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from adminsortable2.admin import SortableAdminBase

from keyta.admin.base_admin import BaseAdmin, BaseQuickAddAdmin
from keyta.admin.base_inline import (
    BaseTabularInline,
    SortableTabularInlineWithDelete,
    TabularInlineWithDelete,
)
from keyta.admin.list_filters import SystemListFilter, WindowListFilter
from keyta.apps.keywords.models import TestStep
from keyta.apps.systems.models import System
from keyta.apps.windows.models import Window
from keyta.forms import form_with_select
from keyta.widgets import BaseSelect, link, CheckboxSelectMultipleSystems

from ..forms import VariableForm, VariableQuickAddForm
from ..models import (
    Variable,
    VariableDocumentation,
    VariableQuickAdd,
    VariableQuickChange,
    VariableValue,
    VariableWindowRelation
)


class Values(SortableTabularInlineWithDelete):
    fk_name = 'variable'
    model = VariableValue
    fields = ['name', 'value']
    extra = 0
    min_num = 1

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'value':
            field.widget = forms.TextInput(attrs={
                'style': 'width: 100%',
                'placeholder': _('Wert eintragen, anschließend Tab drücken')
            })

        return field

    def has_delete_permission(self, request, obj=None):
        return self.can_change(request.user, 'variable')


class Windows(TabularInlineWithDelete):
    model = VariableWindowRelation
    extra = 0
    fields = ['window']
    tab_name = _('Masken').lower()
    verbose_name = _('Maske')
    verbose_name_plural = _('Masken')

    form = form_with_select(
        VariableWindowRelation,
        'window',
        _('Maske auswählen'),
        labels={
            'window': _('Maske')
        }
    )

    def get_formset(self, request, obj=None, **kwargs):
        variable: Variable = obj
        systems = variable.systems.all()
        windows = Window.objects.filter(systems__in=systems).distinct()
        
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['window'].queryset = windows

        return formset

    def has_change_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Variable)
class VariableAdmin(SortableAdminBase, BaseAdmin):
    list_display = ['name', 'description', 'system_list']
    list_display_links = ['name']
    list_filter = [
        ('systems', SystemListFilter),
        ('windows', WindowListFilter)
    ]
    search_fields = ['name', 'description']
    search_help_text = _('Name')

    form = form_with_select(
        Variable,
        'type',
        '',
        form_class=VariableForm
    )
    inlines = [Values]

    @admin.display(description=_('Systeme'))
    def system_list(self, window: Window):
        return ', '.join(
            window.systems.values_list('name', flat=True)
        )

    def autocomplete_name_queryset(self, name: str, request: HttpRequest):
        return super().autocomplete_name_queryset(name, request).filter(windows__isnull=True)

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        if 'quick_change' in request.GET:
            variable = VariableQuickChange.objects.get(id=object_id)
            return HttpResponseRedirect(variable.get_admin_url() + '?_popup=1')

        if 'view' in request.GET:
            variable_doc = VariableDocumentation.objects.get(id=object_id)
            return HttpResponseRedirect(variable_doc.get_admin_url())

        return super().change_view(request, object_id, form_url, extra_context)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'systems':
            field = ModelMultipleChoiceField(
                widget=CheckboxSelectMultipleSystems,
                queryset=field.queryset
            )
            field.label = _('Systeme')

            if variable_id := request.resolver_match.kwargs.get('object_id'):
                variable = Variable.objects.get(id=variable_id)
                window_systems = variable.windows.values_list('systems__pk', flat=True)

                if window_systems.exists():
                    disabled_systems = System.objects.exclude(pk__in=window_systems)
                    field.widget.disabled = set(disabled_systems.values_list('pk', flat=True))

        return field

    def get_fields(self, request, obj=None):
        variable: Variable = obj

        fields = ['systems']

        if variable and variable.windows.count() == 1 and not variable.template:
            fields += ['window']

        fields += ['name', 'description', 'type']

        return fields

    def get_protected_objects(self, obj):
        variable: Variable = obj
        return list(variable.values.all()) + list(TestStep.objects.filter(variable=variable))

    def get_readonly_fields(self, request, obj=None):
        variable: Variable = obj

        fields = []

        if variable and variable.windows.count() == 1:
            fields += ['window']

        return fields

    def has_add_permission(self, request):
        return self.can_add(request.user, 'variable')

    def has_change_permission(self, request, obj=None):
        return self.can_change(request.user, 'variable')

    def has_delete_permission(self, request, obj=None):
        return self.can_delete(request.user, 'variable')

    @admin.display(description=_('Maske'))
    def window(self, variable: Variable):
        window: Window = variable.windows.first()

        return link(
            window.get_admin_url(),
            window.name,
            new_page=True
        )


@admin.register(VariableQuickAdd)
class VariableQuickAddAdmin(SortableAdminBase, BaseQuickAddAdmin):
    fields = ['systems', 'windows', 'name', 'type']
    form = VariableQuickAddForm
    inlines = [Values]

    def autocomplete_name_queryset(self, name: str, request: HttpRequest):
        queryset = super().autocomplete_name_queryset(name, request)

        if 'windows' in request.GET:
            queryset = queryset.filter(windows__in=[request.GET['windows']])

        return queryset

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'type':
            field.widget = BaseSelect('', choices=field.choices)

        return field


class DictionaryValues(BaseTabularInline):
    fk_name = 'variable'
    model = VariableValue
    fields = ['name', 'value']
    readonly_fields = ['name']
    verbose_name = ''
    verbose_name_plural = ''
    max_num = 0

    @admin.display(description=_('Wert'))
    def current_value(self, variable_value: VariableValue):
        return variable_value.current_value


@admin.register(VariableQuickChange)
class VariableQuickChangeAdmin(BaseAdmin):
    def get_fields(self, request, obj=None):
        return []

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        inline_instances.append(DictionaryValues(self.model, self.admin_site))

        return inline_instances

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(VariableDocumentation)
class VariableDocumentationAdmin(VariableQuickChangeAdmin):
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(VariableWindowRelation)
class VariableWindowAdmin(BaseAdmin):
    pass
