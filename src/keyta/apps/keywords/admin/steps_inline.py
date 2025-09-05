from keyta.admin.base_inline import DeleteRelatedField, SortableTabularInline

from ..forms import StepsForm
from ..models import Keyword, KeywordCall
from .field_parameters import ParameterFields
from .field_keywordcall_args import KeywordCallArgsField


class StepsInline(
    DeleteRelatedField,
    ParameterFields,
    KeywordCallArgsField,
    SortableTabularInline
):
    model = KeywordCall
    fk_name = 'from_keyword'
    fields = ['to_keyword']
    form = StepsForm
    extra = 0

    def has_delete_permission(self, request, obj=None):
        keyword: Keyword = obj

        if keyword and keyword.is_action:
            return self.can_change(request.user, 'action')

        if keyword and keyword.is_sequence:
            self.can_change(request.user, 'sequence')

        return super().has_delete_permission(request, obj)
