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
    fields = ['window', 'to_keyword']
    extra = 0 # necessary for saving, since to_keyword is not nullable and is null in an extra
    form = TestStepsForm
    formset = TestStepsFormset

    def get_fields(self, request, obj=None):
        *fields, delete = super().get_fields(request, obj)
        return [*fields, 'variable', delete]
