from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline

from ..forms import KeywordCallParameterFormsetWithErrors
from ..models import KeywordCall, KeywordCallParameter, KeywordParameterType


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
    formset = KeywordCallParameterFormsetWithErrors
    extra = 0
    max_num = 0
    can_delete = False

    def get_fields(self, request, obj=None):
        if not self.has_change_permission(request, obj):
            return ['name', 'readonly_value']

        return ['name', 'value']

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(parameter__type=KeywordParameterType.VARARG)

    def get_readonly_fields(self, request, obj=None):
        if not self.has_change_permission(request, obj):
            return ['name', 'readonly_value']

        return ['name']

    def has_change_permission(self, request, obj=None):
        keywordcall: KeywordCall = obj

        if keywordcall and keywordcall.testcase:
            return True

        if keywordcall and keywordcall.from_keyword:
            return self.can_change(request.user, 'action') or self.can_change(request.user, 'sequence')

        return super().has_change_permission(request, obj)

    @admin.display(description=_('Wert'))
    def readonly_value(self, obj):
        kw_call_parameter: KeywordCallParameter = obj
        return kw_call_parameter.current_value
