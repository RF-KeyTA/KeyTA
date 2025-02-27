from django import forms
from django.contrib import admin
from django.db.models.functions import Lower
from django.http import HttpRequest
from django.utils.translation import gettext as _

from adminsortable2.admin import SortableAdminBase

from keyta.forms import form_with_select
from keyta.models.variable import AbstractVariable

from apps.variables.models import (
    Variable,
    VariableQuickAdd,
    VariableSchemaField,
    VariableValue,
    VariableInList,
    VariableWindowRelation,
)
from apps.windows.models import Window

from .base_admin import BaseAdmin
from .base_inline import TabularInlineWithDelete, SortableTabularInlineWithDelete
from .window import QuickAddMixin


class ListElements(QuickAddMixin, SortableTabularInlineWithDelete):
    model = VariableInList
    fk_name = 'list_variable'
    fields = ['variable']
    form = forms.modelform_factory(
        VariableInList,
        fields=['variable']
    )
    quick_add_field = 'variable'
    quick_add_model = VariableQuickAdd
    verbose_name = _('Referenzwert')
    verbose_name_plural = _('Referenzwerte')

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('variable__name')

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def quick_add_url_params(self, request: HttpRequest):
        variable_id = request.resolver_match.kwargs['object_id']
        variable = Variable.objects.get(pk=variable_id)
        window_id = variable.windows.first().pk
        system_id = variable.systems.first().pk
        schema_id = variable.schema.pk

        return {
            'windows': window_id,
            'systems': system_id,
            'schema': schema_id,
            'type': 'DICT',
            'list_id': variable_id
        }


class Values(TabularInlineWithDelete):
    model = VariableValue
    fields = ['name', 'value']
    extra = 0
    min_num = 1

    def get_max_num(self, request, obj=None, **kwargs):
        variable: Variable = obj

        if variable.schema:
            return 0

        return super().get_max_num(request, obj, **kwargs)

    def get_fields(self, request, obj=None):
        variable: Variable = obj

        if variable.schema:
            return self.fields

        return super().get_fields(request, obj)

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        variable: Variable = obj

        if variable.schema:
            return ['name']

        return super().get_readonly_fields(request, obj)


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
        variable: AbstractVariable = obj
        variable_systems = variable.systems.all()
        windows = Window.objects.filter(systems__in=variable_systems).distinct()
        
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['window'].queryset = windows

        return formset

    def has_change_permission(self, request, obj=None) -> bool:
        return False

# TODO: If variable.in_list then show variable.in_list.list_variable
class BaseVariableAdmin(SortableAdminBase, BaseAdmin):
    list_display = ['system_list', 'name', 'description']
    list_display_links = ['name']
    list_filter = ['systems']
    ordering = [Lower('name')]
    search_fields = ['name']
    search_help_text = _('Name')

    @admin.display(description=_('Systeme'))
    def system_list(self, obj):
        variable: AbstractVariable = obj

        if not variable.systems.exists():
            return _('System unabhängig')

        return list(variable.systems.values_list('name', flat=True))

    fields = ['systems', 'name', 'description']
    form = form_with_select(
        Variable,
        'systems',
        _('System hinzufügen'),
        select_many=True
    )
    inlines = [Values]

    def get_fields(self, request, obj=None):
        variable: Variable = obj

        fields = []

        if variable.schema:
            fields += ['schema']

        return super().get_fields(request, obj) + fields

    def get_inlines(self, request, obj):
        variable: AbstractVariable = obj

        if not variable or not variable.systems.exists():
            return []

        if variable.type == 'DICT':
            return [Values]

        if variable.type == 'LIST':
            return [ListElements]

    def get_readonly_fields(self, request, obj=None):
        variable: Variable = obj

        if variable.schema:
            return ['schema']

        return []


class SchemaFields(TabularInlineWithDelete):
    model = VariableSchemaField
    fields = ['name']
    min_num = 1


class BaseVariableSchemaAdmin(BaseAdmin):
    fields = ['name']
    inlines = [SchemaFields]
