from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from keyta.apps.keywords.admin import StepsInline
from keyta.apps.keywords.forms import StepsForm
from keyta.apps.keywords.models import KeywordCall
from keyta.forms import form_with_select

from ..forms import SequenceStepsFormset


class SequenceSteps(StepsInline):
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
        return ['execute'] + super().get_fields(request, obj)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'execute':
            field.label = mark_safe('<span title="%s">▶</span>' % _('Ausführen ab'))

        return field
