import json

from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models.functions import Lower
from django.forms import HiddenInput
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.translation import gettext as _

from adminsortable2.admin import SortableAdminBase, CustomInlineFormSet

from keyta.forms import form_with_select
from keyta.models.variable import AbstractVariable, VariableType
from keyta.widgets import BaseSelect, link, Icon

from apps.variables.models import (
    Variable,
    VariableDocumentation,
    VariableInList,
    VariableQuickAdd,
    VariableQuickChange,
    VariableSchemaField,
    VariableValue,
    VariableWindowRelation,
)
from apps.windows.models import Window

from .base_admin import BaseAdmin, BaseQuickAddAdmin
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
    fields = ['variable', 'view']
    quick_add_field = 'variable'
    quick_add_model = VariableQuickAdd
    verbose_name = _('Referenzwert')
    verbose_name_plural = _('Referenzwerte')

    @admin.display(description='')
    def view(self, obj: VariableInList):
        return link(
            obj.variable.get_admin_url(),
            str(Icon(settings.FA_ICONS.view, {'font-size': '18px', 'margin-top': '10px'}))
        )

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        return super().get_readonly_fields(request, obj) + ['view']

    def quick_add_url_params(self, request: HttpRequest):
        variable_id = request.resolver_match.kwargs['object_id']
        variable = Variable.objects.get(pk=variable_id)
        window_id = variable.windows.first().pk
        system_id = variable.systems.first().pk
        schema_id = variable.schema.pk
        window = Window.objects.get(pk=window_id)
        tab_url = window.get_tab_url(getattr(self, 'tab_name', None))

        return {
            'windows': window_id,
            'systems': system_id,
            'schema': schema_id,
            'type': VariableType.DICT,
            'list_id': variable_id,
            'ref': request.path + tab_url
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

    def autocomplete_name(self, name: str, request: HttpRequest):
        queryset = (
            self.model.objects
            .filter(name__icontains=name)
            .filter(windows__isnull=True)
        )

        names = list(queryset.values_list('name', flat=True))

        return json.dumps(names)

    def get_queryset(self, request: HttpRequest):
        queryset = super().get_queryset(request)

        if request.path == '/variables/variable/':
            return queryset.filter(in_list__isnull=True)

        return queryset

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        if 'quick_change' in request.GET:
            variable = VariableQuickChange.objects.get(id=object_id)
            return HttpResponseRedirect(variable.get_admin_url())

        if 'view' in request.GET:
            variable_doc = VariableDocumentation.objects.get(id=object_id)
            return HttpResponseRedirect(variable_doc.get_admin_url())

        return super().change_view(request, object_id, form_url, extra_context)

    form = form_with_select(
        Variable,
        'systems',
        _('System hinzufügen'),
        select_many=True
    )
    inlines = [Values]

    def get_fields(self, request, obj=None):
        variable: Variable = obj

        fields = ['systems']

        if variable and variable.windows.count() == 1:
            fields += ['window']

        fields += ['name', 'description']

        if variable and variable.schema:
            fields += ['schema']

        if variable and variable.in_list.exists():
            fields += ['in_list']

        return fields

    def get_inlines(self, request, obj):
        variable: AbstractVariable = obj

        if variable and variable.type == VariableType.LIST:
            return [ListElements]

        return self.inlines

    def get_readonly_fields(self, request, obj=None):
        variable: Variable = obj

        fields = []

        if variable and variable.windows.count() == 1:
            fields += ['window']

        if variable and variable.schema:
            fields += ['schema']

        if variable and variable.in_list.exists():
            fields += ['in_list']

        return fields

    @admin.display(description=_('Maske'))
    def window(self, variable: Variable):
        window = variable.windows.first()

        return link(
            window.get_admin_url(),
            window.name
        )

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

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'name':
            field.widget.attrs.update({'style': 'width: 100%'})

        return field


class BaseVariableSchemaAdmin(BaseAdmin):
    fields = ['name']
    inlines = [SchemaFields]


class BaseVariableSchemaQuickAddAdmin(BaseQuickAddAdmin):
    fields = ['windows', 'name']
    inlines = [SchemaFields]


class BaseVariableQuickAddAdmin(BaseQuickAddAdmin):
    fields = ['systems', 'windows', 'name', 'schema', 'type']

    def autocomplete_name(self, name: str, request: HttpRequest):
        queryset = self.model.objects.filter(name__icontains=name)
        
        if 'list_id' in request.GET:
            queryset = queryset.filter(in_list__list_variable=request.GET['list_id'])
        else:
            queryset = queryset.filter(in_list__isnull=True)

        if 'windows' in request.GET:
            queryset = queryset.filter(windows__in=[request.GET['windows']])

        names = list(queryset.values_list('name', flat=True))

        return json.dumps(names)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'schema':
            if 'list_id' in request.GET:
                field.widget = HiddenInput()
            else:
                field.widget = BaseSelect('')
                
                if 'windows' in request.GET:
                    field.queryset = field.queryset.filter(windows__in=request.GET['windows'])

        if db_field.name == 'type':
            if 'list_id' in request.GET:
                field.widget = HiddenInput()
            else:
                field.widget = BaseSelect('', choices=field.choices)

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

            if schema := variable.schema:
                for field in schema.fields.all():
                    variable.add_value(field, list_variable)


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
        return variable_value.current_value()


class ListValues(BaseTabularInline):
    fk_name = 'list_variable'
    model = VariableValue
    fields = ['name', 'value']
    readonly_fields = ['name']
    max_num = 0

    def get_queryset(self, request):
        return super().get_queryset(request).filter(variable=self.variable_pk)


class BaseVariableQuickChangeAdmin(BaseAdmin):
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
        return True

    def has_delete_permission(self, request, obj=None):
        return False


class BaseVariableDocumentationAdmin(BaseVariableQuickChangeAdmin):
    def has_change_permission(self, request, obj=None):
        return False
