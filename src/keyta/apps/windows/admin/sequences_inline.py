from django.utils.translation import gettext_lazy as _

from forms import form_with_select
from keyta.apps.keywords.models import KeywordWindowRelation
from keyta.apps.sequences.models import SequenceQuickAdd

from ..forms import QuickAddFormset
from .window_keyword_inline import WindowKeywordInline


class SequenceFormset(QuickAddFormset):
    def quick_add_field(self) -> str:
        return 'keyword'

    def quick_add_model(self):
        return SequenceQuickAdd


class Sequences(WindowKeywordInline):
    form = form_with_select(
        KeywordWindowRelation,
        'keyword',
        '',
        labels={
            'keyword': _('Sequenz')
        }
    )
    formset = SequenceFormset
    verbose_name = _('Sequenz')
    verbose_name_plural = _('Sequenzen')

    def get_queryset(self, request):
        return super().get_queryset(request).sequences()
