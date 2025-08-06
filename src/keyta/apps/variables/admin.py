import json

from django import forms
from django.conf import settings
from django.contrib import admin
from django.forms import HiddenInput, MultipleHiddenInput
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from adminsortable2.admin import SortableAdminBase, CustomInlineFormSet

from keyta.admin.base_admin import BaseAdmin, BaseQuickAddAdmin
from keyta.admin.base_inline import (
    BaseTabularInline,
    SortableTabularInlineWithDelete,
    TabularInlineWithDelete,
)
from keyta.admin.list_filters import SystemListFilter, WindowListFilter
from keyta.apps.windows.admin import QuickAddMixin
from keyta.apps.windows.models import Window
from keyta.forms import form_with_select, BaseForm
from keyta.widgets import BaseSelect, link

from .models import (
    Variable,
    VariableDocumentation,
    VariableInList,
    VariableQuickAdd,
    VariableQuickChange,
    VariableSchema,
    VariableSchemaField,
    VariableType,
    VariableValue,
    VariableWindowRelation, VariableSchemaQuickAdd,
)


class ListElementsFormset(CustomInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        # Extra forms have index None
        if index is not None:
            form.fields['variable'].widget = HiddenInput()


class ListElements(QuickAddMixin, SortableTabularInlineWithDelete):
    model = VariableInList
    fk_name = 'list_variable'
    formset = ListElementsFormset
    fields = ['variable', 'variable_link']
    quick_add_field = 'variable'
    quick_add_model = VariableQuickAdd
    verbose_name = _('Referenzwert')
    verbose_name_plural = _('Referenzwerte')

    @admin.display(description='')
    def variable_link(self, obj: VariableInList):
        return link(
            obj.variable.get_admin_url(),
            obj.variable.name
        )

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        return super().get_readonly_fields(request, obj) + ['variable_link']

    # Sortable inlines need change permission
    def has_change_permission(self, request, obj=None) -> bool:
        return True

    def quick_add_url_params(self, request: HttpRequest, url_params: dict):
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

    def get_fields(self, request, obj=None):
        variable: Variable = obj

        # If the variable has a schema, the values cannot be deleted
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
        variable: Variable = obj
        systems = variable.systems.all()
        windows = Window.objects.filter(systems__in=systems).distinct()
        
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['window'].queryset = windows

        return formset

    def has_change_permission(self, request, obj=None) -> bool:
        return False


class VariableForm(BaseForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        systems = self.cleaned_data.get('systems')
        variable_systems = [
            system.name
            for system in self.initial.get('systems', [])
        ]

        if systems:
            if system := systems.values_list('name', flat=True).exclude(name__in=variable_systems).filter(variables__name=name).first():
                variable = self._meta.model.objects.filter(name=name).filter(systems__name=system).filter(windows__isnull=True)
                if variable.exists():
                    raise forms.ValidationError(
                        {
                            "name": _(f'Eine Variable mit diesem Namen existiert bereits im System "{system}"')
                        }
                    )


@admin.register(Variable)
class VariableAdmin(SortableAdminBase, BaseAdmin):
    list_display = ['name', 'description', 'system_list']
    list_display_links = ['name']
    list_filter = [
        ('systems', SystemListFilter),
        ('windows', WindowListFilter)
    ]
    search_fields = ['name']
    search_help_text = _('Name')

    form = form_with_select(
        Variable,
        'systems',
        _('System hinzufügen'),
        form_class=VariableForm,
        select_many=True
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
            return HttpResponseRedirect(variable.get_admin_url())

        if 'view' in request.GET:
            variable_doc = VariableDocumentation.objects.get(id=object_id)
            return HttpResponseRedirect(variable_doc.get_admin_url())

        return super().change_view(request, object_id, form_url, extra_context)

    def get_fields(self, request, obj=None):
        variable: Variable = obj

        fields = ['systems']

        if variable and variable.windows.count() == 1 and not variable.template:
            fields += ['window']

        fields += ['name', 'description']

        if variable and variable.schema:
            fields += ['schema']

        if variable and variable.in_list.exists():
            fields += ['in_list']

        return fields

    def get_inlines(self, request, obj):
        variable: Variable = obj

        if variable and variable.type == VariableType.LIST:
            return [ListElements]

        return self.inlines

    def get_queryset(self, request: HttpRequest):
        queryset = super().get_queryset(request)

        # In the list view do not show variables that belong to a list variable
        if request.path == '/variables/variable/':
            return queryset.filter(in_list__isnull=True)

        return queryset

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

    @admin.display(description=_('Tabelle'))
    def in_list(self, variable: Variable):
        if in_list := variable.in_list.first():
            return link(
                in_list.list_variable.get_admin_url(),
                str(in_list.list_variable)
            )

    @admin.display(description=_('Maske'))
    def window(self, variable: Variable):
        window: Window = variable.windows.first()

        return link(
            window.get_admin_url(app=settings.WINDOWS_APP),
            window.name
        )


class SchemaFields(SortableTabularInlineWithDelete):
    model = VariableSchemaField
    fields = ['name']
    min_num = 1

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'name':
            field.widget.attrs.update({'style': 'width: 100%'})

        return field


@admin.register(VariableSchema)
class VariableSchemaAdmin(SortableAdminBase, BaseAdmin):
    fields = ['name']
    inlines = [SchemaFields]

    def get_fields(self, request, obj=None):
        schema: VariableSchema = obj

        if schema:
            return ['window'] + self.fields

        return self.fields

    def get_readonly_fields(self, request, obj=None):
        schema: VariableSchema = obj

        if schema:
            return ['window'] + super().get_readonly_fields(request, obj)

        return super().get_readonly_fields(request, obj)

    @admin.display(description=_('Maske'))
    def window(self, schema: VariableSchema):
        window = schema.windows.first()

        return link(
            window.get_admin_url(),
            window.name
        )


@admin.register(VariableSchemaQuickAdd)
class VariableSchemaQuickAddAdmin(SortableAdminBase, BaseQuickAddAdmin):
    fields = ['windows', 'name']
    inlines = [SchemaFields]


class QuickAddVariableForm(BaseForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        windows = self.cleaned_data.get('windows')

        if len(windows) == 1:
            window = windows[0]
            if window.variables.filter(name=name).exists():
                raise forms.ValidationError(
                    {
                        "name": _(f'Eine Variable mit diesem Namen existiert bereits in der Maske "{window.name}"')
                    }
                )


@admin.register(VariableQuickAdd)
class VariableQuickAddAdmin(BaseQuickAddAdmin):
    fields = ['systems', 'windows', 'name', 'schema', 'type']
    form = QuickAddVariableForm

    def autocomplete_name_queryset(self, name: str, request: HttpRequest):
        queryset = super().autocomplete_name_queryset(name, request)
        
        if 'list_id' in request.GET:
            queryset = queryset.filter(in_list__list_variable=request.GET['list_id'])
        else:
            queryset = queryset.filter(in_list__isnull=True)

        if 'windows' in request.GET:
            queryset = queryset.filter(windows__in=[request.GET['windows']])

        return queryset

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'schema':
            if 'list_id' in request.GET:
                field.widget = HiddenInput()
            else:
                field.widget = BaseSelect('')
                
                if 'windows' in request.GET:
                    field.queryset = field.queryset.filter(windows__in=[request.GET['windows']])

        if db_field.name == 'systems':
            if 'list_id' in request.GET:
                field.widget = MultipleHiddenInput()

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
        return variable_value.current_value

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('schema_field__index')

class ListValues(BaseTabularInline):
    fk_name = 'list_variable'
    model = VariableValue
    fields = ['name', 'value']
    readonly_fields = ['name']
    max_num = 0

    def get_queryset(self, request):
        return super().get_queryset(request).filter(variable=self.variable_pk).order_by('schema_field__index')


@admin.register(VariableQuickChange)
class VariableQuickChangeAdmin(BaseAdmin):
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


@admin.register(VariableDocumentation)
class VariableDocumentationAdmin(VariableQuickChangeAdmin):
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(VariableInList)
class VariableInListAdmin(BaseAdmin):
    pass


@admin.register(VariableSchemaField)
class VariableSchemaFieldAdmin(BaseAdmin):
    pass


@admin.register(VariableValue)
class VariableValueAdmin(BaseAdmin):
    pass


@admin.register(VariableWindowRelation)
class VariableWindowAdmin(BaseAdmin):
    pass
