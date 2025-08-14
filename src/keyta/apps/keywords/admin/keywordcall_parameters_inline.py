from django import forms

from keyta.admin.base_inline import BaseTabularInline

from ..forms import KeywordCallParameterFormset
from ..models import KeywordCallParameter, KeywordParameterType


class KeywordCallParametersForm(forms.ModelForm):
    def save(self, commit=True):
        # Remove the errors set in the method form_errors of UserInputFormset
        # before saving
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

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(parameter__type=KeywordParameterType.VARARG)
