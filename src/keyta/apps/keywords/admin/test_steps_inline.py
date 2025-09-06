from keyta.admin.base_inline import SortableTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField

from ..forms import TestStepsForm, TestStepsFormset
from ..models import KeywordCall
from .field_keywordcall_args import KeywordCallArgsField


class TestStepsInline(   
    DeleteRelatedField,
    KeywordCallArgsField, 
    SortableTabularInline
):
    model = KeywordCall
    fk_name = 'testcase'
    fields = ['execute', 'window', 'to_keyword']
    extra = 0 # necessary for saving, since to_keyword is not nullable and is null in an extra
    form = TestStepsForm
    formset = TestStepsFormset

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('to_keyword')
            .prefetch_related('to_keyword__parameters')
            .prefetch_related('to_keyword__return_values')
        )

    def has_delete_permission(self, request, obj=None):
        return self.can_change(request.user, 'testcase')
