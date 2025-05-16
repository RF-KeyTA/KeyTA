from django import forms
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from keyta.apps.keywords.models.keyword import Keyword
from keyta.apps.resources.models.resource_import import ResourceImport
from keyta.widgets import ModelSelect2AdminWidget

from keyta.apps.variables.models import Variable
from keyta.apps.windows.models import Window

from ..models import KeywordCall
from .steps_form import StepsForm


class KeywordSelectWidget(ModelSelect2AdminWidget):
    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        sequences: QuerySet = super().filter_queryset(request, term, queryset, **dependent_fields)
        window_id = dependent_fields['windows']
        resource_ids = ResourceImport.objects.filter(window_id=window_id).values_list('resource')
        
        # The QuerySet returned by the super class is unique
        # A unique QuerySet can only be combined with a unique QuerySet
        return sequences | Keyword.objects.filter(resource__in=resource_ids).distinct()


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
        'to_keyword': KeywordSelectWidget(
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
