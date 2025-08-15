from keyta.admin.base_inline import SortableTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.apps.keywords.models import Keyword
from keyta.apps.resources.models import ResourceImport
from keyta.apps.testcases.models import TestCase
from keyta.apps.windows.models import Window
from keyta.widgets import quick_change_widget

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

    def get_formset(self, request, obj=None, **kwargs):
        testcase: TestCase = obj
        systems = testcase.systems.all()
        windows = (
            Window.objects
            .filter(systems__in=systems)
            .distinct()
        )
        resource_ids = (
            ResourceImport.objects
            .filter(window__in=windows)
            .values_list('resource')
            .distinct()
        )

        formset = super().get_formset(request, obj, **kwargs)

        window_field = formset.form.base_fields['window']
        window_field.queryset = windows
        window_field.widget = quick_change_widget(window_field.widget)

        to_keyword_field = formset.form.base_fields['to_keyword']
        to_keyword_field.queryset = (
            Keyword.objects.sequences().filter(systems__in=systems) |
            Keyword.objects.filter(resource__in=resource_ids)
        ).distinct().order_by('name')

        variable_field = formset.form.base_fields['variable']
        variable_field.queryset = (
            variable_field.queryset
            .filter(systems__in=systems)
        ).distinct().order_by('name')
        variable_field.widget = quick_change_widget(variable_field.widget)

        return formset
