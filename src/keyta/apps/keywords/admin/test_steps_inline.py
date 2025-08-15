from adminsortable2.admin import CustomInlineFormSet
from django.forms.widgets import Widget

from keyta.admin.base_inline import SortableTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.apps.keywords.models import Keyword
from keyta.apps.resources.models import ResourceImport
from keyta.apps.testcases.models import TestCase
from keyta.apps.windows.models import Window
from keyta.widgets import quick_change_widget

from ..forms import TestStepsForm
from ..models import KeywordCall
from .field_keywordcall_args import KeywordCallArgsField


class LabelWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return '<p>-</p>'


class TestStepsFormset(CustomInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        test_step: KeywordCall = form.instance

        # The index of an extra form is None
        if index is not None and test_step.pk:
            if not test_step.to_keyword:
                form.fields['to_keyword'].widget.can_change_related = False

            if not test_step.variable:
                form.fields['variable'].widget.can_change_related = False

            if not test_step.parameters.exists():
                form.fields['variable'].widget = LabelWidget()

            form.fields['to_keyword'].widget = quick_change_widget(
                form.fields['to_keyword'].widget,
                url_params={'tab_name': test_step.get_tab_url().removeprefix('#')}
            )
            form.fields['to_keyword'].widget.can_add_related = False
            form.fields['to_keyword'].widget.can_change_related = True


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
