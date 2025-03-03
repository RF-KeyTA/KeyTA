from django import forms
from django.contrib import admin
from django.db.models.functions import Lower
from django.forms import HiddenInput
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.translation import gettext as _

from adminsortable2.admin import SortableAdminBase, CustomInlineFormSet

from keyta.forms import form_with_select
from keyta.models.variable import AbstractVariable
from keyta.widgets import BaseSelect, link

from apps.variables.models import (
    Variable,
    VariableDocumentation,
    VariableInList,
    VariableQuickAdd,
    VariableSchemaField,
    VariableValue,
    VariableWindowRelation,
)
from apps.windows.models import Window

from .base_admin import BaseAdmin
from .base_inline import TabularInlineWithDelete, SortableTabularInlineWithDelete, BaseTabularInline
from .window import QuickAddMixin


class ListElementsFormset(CustomInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        variable_field = form.fields['variable']

        # Extra forms have index None
        if index is not None:
            form.fields['variable'] = forms.ModelChoiceField(
                variable_field.queryset,
                disabled=True,
                widget=BaseSelect('')
            )


class ListElements(QuickAddMixin, SortableTabularInlineWithDelete):
    model = VariableInList
    fk_name = 'list_variable'
    formset = ListElementsFormset
    fields = ['variable']
    quick_add_field = 'variable'
    quick_add_model = VariableQuickAdd
    verbose_name = _('Referenzwert')
    verbose_name_plural = _('Referenzwerte')

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
    fk_name = 'variable'
    model = VariableValue
    fields = ['name', 'value']
    extra = 0
    min_num = 1

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'value':
            field.required = False

        return field

    def get_fields(self, request, obj=None):
        variable: Variable = obj

        if variable and variable.schema:
            return self.fields

        return super().get_fields(request, obj)

    def get_max_num(self, request, obj=None, **kwargs):
        variable: Variable = obj

        if variable and variable.schema:
            return 0

        return super().get_max_num(request, obj, **kwargs)

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        variable: Variable = obj

        if variable and variable.schema:
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

class BaseVariableAdmin(SortableAdminBase, BaseAdmin):
    list_display = ['name', 'description']
    list_display_links = ['name']
    list_filter = ['systems', 'windows']
    ordering = [Lower('name')]
    search_fields = ['name']
    search_help_text = _('Name')

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        if '_to_field' in request.GET:
            variable_doc = VariableDocumentation.objects.get(id=object_id)
            return HttpResponseRedirect(variable_doc.get_admin_url())

        return super().change_view(request, object_id, form_url, extra_context)

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

        fields = self.fields

        if variable.windows.exists():
            fields = ['systems', 'windows', 'name', 'description']

        if variable and variable.schema:
            fields += ['schema']

        if variable.in_list.exists():
            fields += ['in_list']

        return fields

    def get_inlines(self, request, obj):
        variable: AbstractVariable = obj

        if variable and variable.type == 'LIST':
            return [ListElements]

        return self.inlines

    def get_readonly_fields(self, request, obj=None):
        variable: Variable = obj

        fields = []

        if variable.windows.exists():
            fields += ['windows']

        if variable and variable.schema:
            fields += ['schema']

        if variable.in_list.exists():
            fields += ['in_list']

        return fields

    @admin.display(description=_('Tabelle'))
    def in_list(self, variable: Variable):
        if in_list := variable.in_list.first():
            return link(
                in_list.list_variable.get_admin_url(),
                str(in_list.list_variable)
            )


class SchemaFields(TabularInlineWithDelete):
    model = VariableSchemaField
    fields = ['name']
    min_num = 1


class BaseVariableSchemaAdmin(BaseAdmin):
    fields = ['name']
    inlines = [SchemaFields]


class BaseVariableSchemaQuickAddAdmin(BaseAdmin):
    fields = ['windows', 'name']
    inlines = [SchemaFields]

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)

        if db_field.name == 'windows':
            field = forms.ModelMultipleChoiceField(
                field.queryset,
                widget=forms.MultipleHiddenInput
            )

        return field


class BaseVariableQuickAddAdmin(BaseAdmin):
    fields = ['systems', 'windows', 'name', 'schema', 'type']
    form = form_with_select(
        VariableQuickAdd,
        'schema',
        _('Vorlage auswählen')
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)

        if db_field.name in {'systems', 'windows'}:
            field = forms.ModelMultipleChoiceField(
                field.queryset,
                widget=forms.MultipleHiddenInput
            )

        return field

    def formfield_for_dbfield(self, db_field, request: HttpRequest, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'type':
            field = forms.ChoiceField(
                choices=field.choices,
                widget=BaseSelect(_('Variablentyp auswählen'))
            )

        if db_field.name == 'schema':
            windows = request.GET['windows']
            field.queryset = field.queryset.filter(windows__in=[windows])

        if request.GET.get('list_id', None):
            if db_field.name in {'schema', 'type'}:
                field.widget = HiddenInput()

        return field

    def save_model(self, request: HttpRequest, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            variable: Variable = obj
            list_variable = None

            if list_id := request.GET.get('list_id', None):
                list_variable = Variable.objects.get(id=list_id)
                VariableInList.objects.create(
                    list_variable=list_variable,
                    variable=variable
                )

            if variable.schema:
                for field in variable.schema.fields.all():
                    VariableValue.objects.create(
                        list_variable=list_variable,
                        variable=variable,
                        name=field.name
                    )


class DictionaryValues(BaseTabularInline):
    fk_name = 'variable'
    model = VariableValue
    fields = ['name', 'value']
    readonly_fields = ['name', 'value']
    verbose_name = ''
    verbose_name_plural = ''


class ListValues(BaseTabularInline):
    fk_name = 'list_variable'
    model = VariableValue
    fields = ['name', 'value']
    readonly_fields = ['name', 'value']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(variable=self.variable_pk)


class BaseVariableDocumentationAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        return []

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)

        variable: Variable = obj

        if variable.is_dict():
            inline_instances.append(DictionaryValues(self.model, self.admin_site))

        if variable.is_list():
            variables = variable.elements.values_list('variable_id', 'variable__name')

            for variable_pk, variable_name in variables:
                inline_instance = ListValues(self.model, self.admin_site)
                inline_instance.variable_pk = variable_pk
                inline_instance.verbose_name_plural = variable_name
                inline_instances.append(inline_instance)

        return inline_instances

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
