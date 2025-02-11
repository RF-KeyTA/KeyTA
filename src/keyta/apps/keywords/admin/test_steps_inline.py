from django.utils.translation import gettext as _

from keyta.models.testcase import AbstractTestCase

from ..models import TestStep
from ..forms import TestStepsForm
from .steps_inline import StepsInline


class TestStepsInline(StepsInline):
    model = TestStep
    fields = ['window'] + StepsInline.fields
    form = TestStepsForm

    def get_formset(self, request, obj=None, **kwargs):
        testcase: AbstractTestCase = obj
        formset = super().get_formset(request, obj, **kwargs)

        system_ids = testcase.systems.all()
        window_queryset = formset.form.base_fields['window'].queryset
        windows = window_queryset.filter(systems__in=system_ids).distinct().order_by('name')

        formset.form.base_fields['window'].queryset = windows
        formset.form.base_fields['window'].widget.can_add_related = False
        formset.form.base_fields['window'].widget.can_change_related = False

        formset.form.base_fields['to_keyword'].widget.can_add_related = False
        formset.form.base_fields['to_keyword'].widget.can_change_related = False
        formset.form.base_fields['to_keyword'].widget.can_view_related = False
        formset.form.base_fields['to_keyword'].label = _('Sequenz')
        sequences = formset.form.base_fields['to_keyword'].queryset.sequences().filter(systems__in=system_ids)
        formset.form.base_fields['to_keyword'].queryset = sequences

        return formset
