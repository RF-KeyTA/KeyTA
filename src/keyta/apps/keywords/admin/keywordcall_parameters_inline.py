from django import forms

from keyta.admin.base_inline import BaseTabularInline

from ..forms import KeywordCallParameterFormset
from ..models import KeywordCallParameter


class KeywordCallParametersForm(forms.ModelForm):
    def save(self, commit=True):
        self._errors = None
        return super().save(commit=commit)


class KeywordCallParametersInline(BaseTabularInline):
    model = KeywordCallParameter
    fields = ['name', 'value']
    readonly_fields = ['name']
    form = KeywordCallParametersForm
    formset = KeywordCallParameterFormset
    extra = 0
    max_num = 0
    can_delete = False

    def name(self, kw_call_param: KeywordCallParameter):
        name = kw_call_param.name

        if '_' in name:
            return name.replace('_', ' ').title()

        return name
