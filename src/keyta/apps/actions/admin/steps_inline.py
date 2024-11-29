from django import forms
from django.contrib import admin

from apps.actions.models import RobotKeywordCall, Action
from apps.common.widgets import GroupedByLibrary, BaseSelect
from apps.keywords.admin import StepsInline
from apps.keywords.models import (
    Keyword,
    KeywordCall,
    KeywordCallParameterSource,
    KeywordCallParameter
)



class ActionSteps(StepsInline):
    model = RobotKeywordCall
    fk_name = 'from_keyword'

    @admin.display(description='1. Parameter')
    def first_arg(self, obj: KeywordCall):
        first_param: KeywordCallParameter = obj.parameters.first()

        if not first_param:
            return '-'

        value_ref: KeywordCallParameterSource = first_param.value_ref

        if value_ref and (variable_value := value_ref.variable_value):
            return variable_value.name

        return first_param.current_value

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'to_keyword':
            choice_field = forms.ModelChoiceField(
                label='Schlüsselwort',
                queryset=None,
                widget=BaseSelect('Schlüsselwort auswählen')
            )
            choice_field.iterator = GroupedByLibrary
            return choice_field

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        action: Action = obj
        formset = super().get_formset(request, obj, **kwargs)

        keywords = Keyword.objects.filter(library__in=action.library_ids)
        formset.form.base_fields['to_keyword'].queryset = keywords

        return formset
