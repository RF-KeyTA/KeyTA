from django import forms
from django.utils.translation import gettext as _

from keyta.apps.actions.models import RobotKeywordCall, Action
from keyta.apps.keywords.admin import StepsInline
from keyta.apps.keywords.models import Keyword
from keyta.widgets import GroupedByLibrary, BaseSelect


class ActionSteps(StepsInline):
    model = RobotKeywordCall
    fk_name = 'from_keyword'

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'to_keyword':
            choice_field = forms.ModelChoiceField(
                label=_('Schlüsselwort'),
                queryset=None,
                widget=BaseSelect(_('Schlüsselwort auswählen'))
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
