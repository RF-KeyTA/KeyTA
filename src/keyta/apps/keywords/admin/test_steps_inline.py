from django.utils.translation import gettext as _

from keyta.admin.base_inline import SortableTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.apps.keywords.models.keyword import Keyword
from keyta.models.testcase import AbstractTestCase

from apps.windows.models import Window

from ..forms import TestStepsForm
from ..models import TestStep
from .field_keywordcall_args import KeywordCallArgsField


class TestStepsInline(   
    DeleteRelatedField,
    KeywordCallArgsField, 
    SortableTabularInline
):
    model = TestStep
    fk_name = 'testcase'
    fields = ['window', 'to_keyword']
    extra = 1
    form = TestStepsForm

    def get_formset(self, request, obj=None, **kwargs):
        testcase: AbstractTestCase = obj
        systems = testcase.systems.all()
        windows = Window.objects.filter(systems__in=systems).distinct()

        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['window'].queryset = windows
        formset.form.base_fields['to_keyword'].queryset = (
            Keyword.objects.actions() | Keyword.objects.sequences()
        )

        return formset
