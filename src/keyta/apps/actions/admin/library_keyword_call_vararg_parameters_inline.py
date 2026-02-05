from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import TabularInlineWithDelete
from keyta.apps.keywords.json_value import JSONValue
from keyta.apps.keywords.models import (
    KeywordCall,
    KeywordCallParameter,
    KeywordParameterType
)

from ..forms import LibraryKeywordCallVarargFormset


class VarargForm(forms.ModelForm):
    parameter_type = KeywordParameterType.VAR_ARG

    def clean_value(self):
        value = self.cleaned_data['value']
        json_value = JSONValue.from_json(value)

        if not json_value.pk and not json_value.user_input:
            raise ValidationError(_('Das Eingabefeld darf nicht leer bleiben.'))

        return value

    def save(self, commit=True):
        kw_call_parameter: KeywordCallParameter = self.instance
        kw_call = kw_call_parameter.keyword_call
        kw_call_parameter.parameter = kw_call.to_keyword.parameters.filter(type=self.parameter_type).first()

        # Remove the errors set in the method form_errors of UserInputFormset
        # before saving
        self._errors = None
        return super().save(commit)


class VarkwargForm(VarargForm):
    parameter_type = KeywordParameterType.VAR_KWARG


class VarargParametersInline(TabularInlineWithDelete):
    model = KeywordCallParameter
    fields = ['value']
    form = VarargForm
    formset = LibraryKeywordCallVarargFormset
    extra = 0
    parameter_type = KeywordParameterType.VAR_ARG

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'value':
            field.widget = forms.TextInput(attrs={
                'style': 'width: 100%',
                'placeholder': _('Wert eintragen, anschließend Enter drücken')
            })

        return field

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parameter__type=self.parameter_type)

    def has_add_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        keywordcall: KeywordCall = obj

        if keywordcall and keywordcall.from_keyword:
            return self.can_change(request.user, 'action')

        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)


class VarkwargParametersInline(VarargParametersInline):
    form = VarkwargForm
    parameter_type = KeywordParameterType.VAR_KWARG
