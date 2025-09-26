from django.contrib import admin

from keyta.admin.base_inline import SortableTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.apps.keywords.admin.field_keywordcall_values import KeywordCallValuesField

from ..forms import TestStepsForm, TestStepsFormset
from ..models import TestStep


class TestStepsInline(   
    DeleteRelatedField,
    KeywordCallValuesField,
    SortableTabularInline
):
    model = TestStep
    fk_name = 'testcase'
    fields = ['test_step_url', 'execute', 'window', 'to_keyword']
    readonly_fields = ['test_step_url']
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

    @admin.display(description='')
    def test_step_url(self, obj):
        test_step: TestStep = obj

        return test_step.get_admin_url()
