from django import forms
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import TabularInlineWithDelete

from ..forms import LibraryKeywordCallVarargFormset
from ..models import (
    KeywordCall,
    KeywordCallParameter,
    KeywordParameterType
)


class VarargForm(forms.ModelForm):
    def save(self, commit=True):
        kw_call_parameter: KeywordCallParameter = self.instance
        kw_call = kw_call_parameter.keyword_call
        vararg = kw_call.to_keyword.parameters.filter(type=KeywordParameterType.VARARG).first()
        kw_call_parameter.parameter = vararg

        # Remove the errors set in the method form_errors of UserInputFormset
        # before saving
        self._errors = None
        return super().save(commit)


class VarargParametersInline(TabularInlineWithDelete):
    model = KeywordCallParameter
    fields = ['value']
    form = VarargForm
    formset = LibraryKeywordCallVarargFormset
    extra = 0

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'value':
            field.widget = forms.TextInput(attrs={
                'style': 'width: 100%',
                'placeholder': _('Wert eintragen, anschließend Tab drücken')
            })

        return field

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parameter__type=KeywordParameterType.VARARG)

    def has_add_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        keywordcall: KeywordCall = obj

        if keywordcall and keywordcall.from_keyword:
            return self.can_change(request.user, 'action')

        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)
