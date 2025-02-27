from django import forms
from django.contrib import admin
from django.forms import HiddenInput
from django.http import HttpRequest
from django.utils.translation import gettext as _

from forms import form_with_select
from keyta.admin.base_admin import BaseAdmin
from keyta.admin.variable import BaseVariableAdmin, BaseVariableSchemaAdmin, SchemaFields
from widgets import BaseSelect

from .models import (
    Variable,
    VariableQuickAdd,
    VariableSchema,
    VariableSchemaField,
    VariableSchemaQuickAdd,
    VariableValue,
    VariableInList,
    VariableWindowRelation
)


@admin.register(Variable)
class VariableAdmin(BaseVariableAdmin):
    pass


@admin.register(VariableSchema)
class VariableSchemaAdmin(BaseVariableSchemaAdmin):
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


@admin.register(VariableQuickAdd)
class VariableQuickAddAdmin(BaseAdmin):
    fields = ['systems', 'windows', 'name', 'schema', 'type']
    form = form_with_select(
        VariableQuickAdd,
        'schema',
        _('Schema auswählen')
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

        if request.GET.get('list_id', None):
            if db_field.name in {'schema', 'type'}:
                field.widget = HiddenInput()

        return field

    def save_model(self, request: HttpRequest, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            variable: Variable = obj

            if list_id := request.GET.get('list_id', None):
                VariableInList.objects.create(
                    list_variable=Variable.objects.get(id=list_id),
                    variable=variable
                )

            if variable.schema:
                for field in variable.schema.fields.all():
                    VariableValue.objects.create(
                        variable=variable,
                        name=field.name
                    )


@admin.register(VariableSchemaQuickAdd)
class VariableSchemaQuickAddAdmin(BaseAdmin):
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


@admin.register(VariableInList)
class VariableInListAdmin(BaseAdmin):
    pass
