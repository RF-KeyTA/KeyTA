from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import KeywordCall
from .steps_form import StepsForm


TestStepsForm = forms.modelform_factory(
    KeywordCall,
    StepsForm,
    [],
    labels={
        'to_keyword': _('Sequenz')
    }
)

TestStepsForm.fields_can_change_related = ['window', 'to_keyword', 'variable']
