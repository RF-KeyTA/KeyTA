from django import forms
from django.utils.translation import gettext_lazy as _

from keyta.apps.keywords.models import KeywordCall
from keyta.apps.keywords.forms import StepsForm


TestStepsForm = forms.modelform_factory(
    KeywordCall,
    StepsForm,
    [],
    labels={
        'to_keyword': _('Sequenz')
    }
)

TestStepsForm.fields_can_change_related = ['window', 'to_keyword', 'variable']
