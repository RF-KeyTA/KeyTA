from django.utils.translation import gettext as _

from keyta.apps.keywords.admin import StepsInline
from apps.testcases.models import TestCase
from apps.windows.models import Window

from .models import TestStep
from .forms import TestStepsForm


class TestSteps(StepsInline):
    model = TestStep
    fields = ['window'] + StepsInline.fields
    form = TestStepsForm

    def get_formset(self, request, obj=None, **kwargs):
        testcase: TestCase = obj
        formset = super().get_formset(request, obj, **kwargs)

        system_ids = testcase.systems.all()
        windows = Window.objects.filter(systems__in=system_ids).distinct().order_by('name')

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
