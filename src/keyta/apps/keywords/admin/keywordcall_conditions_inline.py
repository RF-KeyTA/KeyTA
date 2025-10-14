from django import forms
from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField

from ..forms import KeywordCallConditionFormset
from ..json_value import JSONValue
from ..models import KeywordCallCondition, KeywordCall


class ConditionForm(forms.ModelForm):
    def clean_expected_value(self):
        expected_value = self.cleaned_data.get('expected_value')
        json_value = JSONValue.from_json(expected_value)

        if not json_value.user_input and not json_value.pk:
            raise forms.ValidationError(_('Dieses Feld ist zwingend erforderlich.'))

        return expected_value


class ConditionsInline(DeleteRelatedField, BaseTabularInline):
    model = KeywordCallCondition
    fields = ['value_ref', 'condition']
    form = ConditionForm
    formset = KeywordCallConditionFormset

    def get_fields(self, request, obj=None):
        if not self.has_change_permission(request, obj):
            return self.fields + ['readonly_expected_value']

        return self.fields + ['expected_value', 'delete']

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        if not self.has_change_permission(request, obj):
            return ['readonly_expected_value']

        return super().get_readonly_fields(request, obj)

    def has_add_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        keywordcall: KeywordCall = obj

        if keywordcall and keywordcall.testcase:
            return self.can_change(request.user, 'testcase')

        if keywordcall and keywordcall.from_keyword:
            return self.can_change(request.user, 'action') or self.can_change(request.user, 'sequence')

        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    @admin.display(description=_('Soll Wert'))
    def readonly_expected_value(self, obj):
        kw_call_condition: KeywordCallCondition = obj
        return kw_call_condition.current_expected_value
