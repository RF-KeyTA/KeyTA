from django.utils.translation import gettext_lazy as _

from forms import form_with_select
from keyta.apps.actions.models import ActionQuickAdd
from keyta.apps.keywords.models import KeywordWindowRelation

from ..forms import QuickAddFormset
from .window_keyword_inline import WindowKeywordInline


class ActionFormset(QuickAddFormset):
    def quick_add_field(self) -> str:
        return 'keyword'

    def quick_add_model(self):
        return ActionQuickAdd


class Actions(WindowKeywordInline):
    form = form_with_select(
        KeywordWindowRelation,
        'keyword',
        '',
        labels={
            'keyword': _('Aktion')
        }
    )
    formset = ActionFormset
    verbose_name = _('Aktion')
    verbose_name_plural = _('Aktionen')

    def get_queryset(self, request):
        return super().get_queryset(request).actions()
