from django.contrib import admin
from django.utils.translation import gettext as _

from ..forms import KeywordCallParameterFormset
from ..models import TestStep, KeywordCall
from .keywordcall import KeywordCallParametersInline, KeywordCallAdmin


class TestStepParameterFormset(KeywordCallParameterFormset):
    def get_choices(self, kw_call: KeywordCall):
        system_ids = list(
            kw_call.testcase.systems.values_list('pk', flat=True)
        )

        return super().get_prev_return_values() + super().get_window_variables(
            [kw_call.window.id],
            system_ids
        )


class TestStepParametersInline(KeywordCallParametersInline):
    formset = TestStepParameterFormset


@admin.register(TestStep)
class TestStepAdmin(KeywordCallAdmin):
    inlines = [TestStepParametersInline]

    @admin.display(description=_('Sequenz'))
    def to_keyword_doc(self, test_step: TestStep):
        return super().to_keyword_doc(test_step)
