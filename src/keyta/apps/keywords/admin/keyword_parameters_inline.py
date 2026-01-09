from django import forms
from django.utils.translation import gettext_lazy as _

from adminsortable2.admin import CustomInlineFormSet

from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.admin.base_inline import SortableTabularInline

from ..models import Keyword, KeywordParameter


class ParameterFormset(CustomInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyword: Keyword = kwargs.get('instance')

    def clean(self):
        for form in self.extra_forms:
            default_value = form.cleaned_data.get('default_value')

            if not default_value and self.keyword.is_in_use:
                raise forms.ValidationError(
                    _('Beim Hinzufügen eines Parameters darf der Standardwert nicht leer sein.')
                )


class ParameterForm(forms.ModelForm):
    def clean_name(self):
        name = self.cleaned_data.get('name')

        if ':' in name:
            raise forms.ValidationError("Doppelpunkt ist im Parameternamen nicht zulässig")

        return name


class ParametersInline(DeleteRelatedField, SortableTabularInline):
    model = KeywordParameter
    fields = ['position', 'name']
    form = ParameterForm
    formset = ParameterFormset
    extra = 0
    verbose_name = _('Parameter')
    verbose_name_plural = _('Parameters')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'default_value':
            field.label = _('Standardwert (optional)')

        if db_field.name == 'name':
            field.widget = forms.TextInput(attrs={
                'style': 'width: 100%',
                'placeholder': _('Name eintragen, anschließend Enter drücken')
            })

        return field

    def get_fields(self, request, obj=None):
        keyword: Keyword = obj

        if keyword and keyword.is_in_use:
            return self.fields + ['default_value', 'delete']

        return super().get_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        keyword: Keyword = obj

        if keyword and keyword.is_action:
            return self.can_change(request.user, 'action')

        if keyword and keyword.is_sequence:
            return self.can_change(request.user, 'sequence')

        return super().has_delete_permission(request, obj)
