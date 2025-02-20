from django import forms
from django.utils.translation import gettext as _

from keyta.apps.keywords.admin import StepsInline
from keyta.apps.keywords.models import Keyword, KeywordCall
from keyta.forms.baseform import form_with_select
from keyta.widgets import GroupedByLibrary

from ..models import RobotKeywordCall, Action


class GroupedChoiceField(forms.ModelChoiceField):
    iterator = GroupedByLibrary


class ActionSteps(StepsInline):
    model = RobotKeywordCall
    form = form_with_select(
        KeywordCall,
        'to_keyword',
        _('Schlüsselwort auswählen'),
        labels={
            'to_keyword': _('Schlüsselwort')
        },
        field_classes={
            'to_keyword': GroupedChoiceField
        }
    )

    def get_formset(self, request, obj=None, **kwargs):
        action: Action = obj
        keywords = Keyword.objects.filter(library__in=action.library_ids)

        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['to_keyword'].queryset = keywords

        return formset
