from django import forms
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
    fields = ['value_ref', 'condition', 'expected_value']
    form = ConditionForm
    formset = KeywordCallConditionFormset

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
