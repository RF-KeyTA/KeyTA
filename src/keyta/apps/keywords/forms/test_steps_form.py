from django import forms
from django.utils.translation import gettext_lazy as _

from keyta.apps.variables.models import Variable
from keyta.apps.windows.models import Window
from keyta.widgets import ModelSelect2AdminWidget

from ..models import Keyword, KeywordCall
from .steps_form import StepsForm


TestStepsForm = forms.modelform_factory(
    KeywordCall,
    StepsForm,
    [],
    labels={
        'to_keyword': _('Sequenz')
    },
    widgets={
        'window': ModelSelect2AdminWidget(
            placeholder=_('Maske auswählen'),
            model=Window,
            search_fields=['name__icontains'],
        ),
        'to_keyword': ModelSelect2AdminWidget(
            placeholder=_('Sequenz auswählen'),
            model=Keyword,
            search_fields=['name__icontains'],
            dependent_fields={'window': 'windows'},
        ),
        'variable': ModelSelect2AdminWidget(
            placeholder=_('Referenzwert auswählen'),
            model=Variable,
            search_fields=['name__icontains'],
            dependent_fields={'window': 'windows'},
            attrs={
                'data-allow-clear': 'true',
            }
        )
    }
)

TestStepsForm.fields_can_change_related = ['window', 'to_keyword', 'variable']
