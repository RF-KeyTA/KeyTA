from django import forms
from django.forms.utils import ErrorDict, ErrorList
from django.utils.translation import gettext_lazy as _

from adminsortable2.admin import CustomInlineFormSet

from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.admin.base_inline import SortableTabularInline

from ..models import Variable, VariableValue


class ValuesFormset(CustomInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variable: Variable = kwargs.get('instance')

    def clean(self):
        names = set()
        values = set()

        for form in self.forms:
            name = form.cleaned_data.get('name')

            if name and name in names:
                form._errors = ErrorDict()
                form._errors['name'] = ErrorList([
                    _('Dieser Name ist bereits vorhanden.')
                ])

            if self.variable.is_list():
                value = form.cleaned_data.get('value')

                if value and value in values:
                    form._errors = ErrorDict()
                    form._errors['value'] = ErrorList([
                        _('Dieser Wert ist bereits vorhanden.')
                    ])

                values.add(value)

            names.add(name)


class Values(DeleteRelatedField, SortableTabularInline):
    fk_name = 'variable'
    model = VariableValue
    extra = 0
    formset = ValuesFormset

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        variable_pk = request.resolver_match.kwargs['object_id']
        variable = Variable.objects.get(pk=variable_pk)

        if db_field.name == 'name':
            field.widget = forms.TextInput(attrs={
                'style': 'width: 100%',
            })

        if db_field.name == 'value':
            field.widget = forms.TextInput(attrs={
                'style': 'width: 100%',
                'placeholder': _('Wert eintragen, anschließend Enter drücken') if variable.is_list() else ''
            })

        return field

    def get_fields(self, request, obj=None):
        fields: list = super().get_fields(request, obj)
        variable: Variable = obj

        if variable and variable.is_list():
            return [
                field
                for field in fields
                if field != 'name'
            ]

        return fields

    def has_delete_permission(self, request, obj=None):
        variable: Variable = obj

        if variable and variable.template:
            return False

        return self.can_change(request.user, 'variable')
