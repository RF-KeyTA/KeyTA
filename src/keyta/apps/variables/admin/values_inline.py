from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from adminsortable2.admin import CustomInlineFormSet

from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.admin.base_inline import SortableTabularInline

from ..models import Variable, VariableValue


class ValuesFormset(CustomInlineFormSet):
    def clean(self):
        names = set()

        for form in self.forms:
            name = form.cleaned_data.get('name')

            if name and name in names:
                raise ValidationError(_('Die Namen müssen eindeutig sein.'))

            names.add(name)


class Values(DeleteRelatedField, SortableTabularInline):
    fk_name = 'variable'
    model = VariableValue
    extra = 0
    formset = ValuesFormset

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'name':
            field.widget = forms.TextInput(attrs={
                'style': 'width: 100%',
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
