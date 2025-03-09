from adminsortable2.admin import CustomInlineFormSet

from keyta.admin.base_inline import SortableTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.apps.keywords.models import Keyword
from keyta.apps.resources.models import ResourceImport
from keyta.models.testcase import AbstractTestCase

from apps.windows.models import Window

from ..forms import TestStepsForm
from ..models import TestStep
from .field_keywordcall_args import KeywordCallArgsField


class TestStepsFormset(CustomInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        test_step: TestStep = form.instance

        # The index of an extra form is None
        if index is not None and test_step.pk:
            if test_step.to_keyword.resource:
                form.fields['to_keyword'].widget.can_change_related = False

            if not test_step.variable:
                form.fields['variable'].widget.can_view_related = False
                form.fields['variable'].widget.can_change_related = False


class TestStepsInline(   
    DeleteRelatedField,
    KeywordCallArgsField, 
    SortableTabularInline
):
    model = TestStep
    fk_name = 'testcase'
    fields = ['window', 'to_keyword']
    extra = 0 # necessary for saving, since to_keyword is not nullable and is null in an extra
    form = TestStepsForm
    formset = TestStepsFormset

    def get_fields(self, request, obj=None):
        *fields, delete = super().get_fields(request, obj)
        return [*fields, 'variable', delete]

    def get_formset(self, request, obj=None, **kwargs):
        testcase: AbstractTestCase = obj
        systems = testcase.systems.all()
        windows = Window.objects.filter(systems__in=systems).distinct().order_by('name')
        resource_ids = ResourceImport.objects.filter(window__in=windows).values_list('resource').distinct()

        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['window'].queryset = windows
        variable_field = formset.form.base_fields['variable']
        variable_field.queryset = variable_field.queryset.filter(in_list__isnull=True).order_by('name')
        to_keyword_field = formset.form.base_fields['to_keyword']
        to_keyword_field.queryset = (
            Keyword.objects.sequences() | 
            Keyword.objects.filter(resource__in=resource_ids)
        ).order_by('name')
        
        return formset
