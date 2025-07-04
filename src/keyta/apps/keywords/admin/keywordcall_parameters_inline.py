from django import forms
from django.utils.translation import gettext as _

from keyta.admin.base_inline import BaseTabularInline

from ..forms import KeywordCallParameterFormset
from ..models import KeywordCallParameter


class KeywordCallParametersForm(forms.ModelForm):
    def save(self, commit=True):
        self._errors = None
        return super().save(commit=commit)


class KeywordCallParametersInline(BaseTabularInline):
    model = KeywordCallParameter
    fields = ['name', 'value', 'robot_variable']
    readonly_fields = ['name']
    form = KeywordCallParametersForm
    formset = KeywordCallParameterFormset
    extra = 0
    max_num = 0
    can_delete = False

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'robot_variable':
            field.widget.attrs['data-placeholder'] = _('Format auswählen')
            field.widget.attrs['data-width'] = '100%'
            field.widget.attrs['data-allow-clear'] = 'true'

        return field

    def name(self, kw_call_param: KeywordCallParameter):
        name = kw_call_param.name

        if '_' in name:
            return name.replace('_', ' ').title()

        return name
