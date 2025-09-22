from keyta.admin.base_inline import SortableTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField

from keyta.apps.keywords.models import KeywordCall
from keyta.apps.keywords.admin.field_keywordcall_values import KeywordCallValuesField

from ..forms import TestStepsForm, TestStepsFormset


class TestStepsInline(   
    DeleteRelatedField,
    KeywordCallValuesField,
    SortableTabularInline
):
    model = KeywordCall
    fk_name = 'testcase'
    fields = ['execute', 'window', 'to_keyword']
    extra = 0 # necessary for saving, since to_keyword is not nullable and is null in an extra
    form = TestStepsForm
    formset = TestStepsFormset
    template = 'test_steps_sortable_tabular.html'

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('to_keyword')
            .prefetch_related('to_keyword__parameters')
            .prefetch_related('to_keyword__return_values')
        )

    def has_delete_permission(self, request, obj=None):
        return self.can_change(request.user, 'testcase')
