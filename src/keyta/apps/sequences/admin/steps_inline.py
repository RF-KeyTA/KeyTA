from django.utils.translation import gettext_lazy as _

from keyta.admin.field_execution_state import ExecutionStateField
from keyta.apps.keywords.admin import StepsInline
from keyta.apps.keywords.forms import StepsForm
from keyta.apps.keywords.models import KeywordCall
from keyta.forms import form_with_select

from ..forms import SequenceStepsFormset


class SequenceSteps(ExecutionStateField, StepsInline):
    model = KeywordCall
    form = form_with_select(
        KeywordCall,
        'to_keyword',
        _('Aktion auswählen'),
        labels={
            'to_keyword': _('Aktion')
        },
        form_class=StepsForm,
        can_change_related=True
    )
    formset = SequenceStepsFormset
    template = 'sequence_steps_sortable_tabular.html'

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)

        if 'split' in request.GET:
            self.template = 'admin/edit_inline/tabular.html'
            return ['enabled'] + ['to_keyword']

        return fields

    def get_max_num(self, request, obj=None, **kwargs):
        if 'split' in request.GET:
            return 0

        return super().get_max_num(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if 'split' in request.GET:
            return []

        return super().get_readonly_fields(request, obj)
