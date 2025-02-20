from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.apps.sequences.models import Sequence
from keyta.widgets import open_link_in_modal

from ..forms import KeywordCallParameterFormset
from ..models import TestStep
from .keyword_call import KeywordCallParametersInline, KeywordCallAdmin


class TestStepParameterFormset(KeywordCallParameterFormset):
    def get_choices(self, kw_call: KeywordCall):
        system_ids = list(
            kw_call.testcase.systems.values_list('pk', flat=True)
        )

        return super().get_prev_return_values() + super().get_window_variables(
            [kw_call.window.id],
            system_ids
        )


class TestStepParameters(KeywordCallParametersInline):
    formset = TestStepParameterFormset


@admin.register(TestStep)
class TestStepAdmin(KeywordCallAdmin):
    def get_inlines(self, request, obj):
        return [TestStepParameters]

    @admin.display(description=_('Sequenz'))
    def keyword_doc(self, obj: TestStep):
        return open_link_in_modal(
            Sequence(obj.to_keyword.pk).get_docadmin_url(),
            obj.to_keyword.name
        )
