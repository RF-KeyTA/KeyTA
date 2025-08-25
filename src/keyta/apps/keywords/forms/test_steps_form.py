from django import forms
from django.utils.translation import gettext_lazy as _

from keyta.apps.keywords.models.keyword import Keyword
from keyta.apps.resources.models.resource_import import ResourceImport
from keyta.apps.variables.models import Variable
from keyta.apps.windows.models import Window
from keyta.widgets import ModelSelect2AdminWidget

from ..models import KeywordCall
from .steps_form import StepsForm


class SequenceSelectWidget(ModelSelect2AdminWidget):
    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        window_id = dependent_fields['windows']
        sequences = Keyword.objects.sequences().filter(windows__in=[window_id]).distinct()
        resource_ids = ResourceImport.objects.filter(window_id=window_id).values_list('resource')
        
        # The QuerySet returned by the super class is unique
        # A unique QuerySet can only be combined with a unique QuerySet
        return sequences | Keyword.objects.filter(resource__in=resource_ids).distinct()


class VariableSelectWidget(ModelSelect2AdminWidget):
    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        return super().filter_queryset(request, term, queryset, **dependent_fields).filter(template='')


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
        'to_keyword': SequenceSelectWidget(
            placeholder=_('Sequenz auswählen'),
            model=Keyword,
            search_fields=['name__icontains'],
            dependent_fields={'window': 'windows'},
        ),
        'variable': VariableSelectWidget(
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
