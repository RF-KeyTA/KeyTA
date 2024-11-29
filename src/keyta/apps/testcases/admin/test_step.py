from django.contrib import admin

from apps.common.widgets import open_link_in_modal
from apps.keywords.admin import KeywordCallParametersInline, KeywordCallAdmin
from apps.keywords.forms import KeywordCallParameterFormset
from apps.sequences.models import Sequence

from ..models.test_step import TestStep


class TestStepParameterFormset(KeywordCallParameterFormset):
    def get_choices(self, obj: TestStep):
        system_ids = list(
            obj.testcase.systems.values_list('pk', flat=True)
        )

        return super().prev_return_values() + super().get_variables(
                [obj.window.id],
                system_ids,
                lambda value_ref: str(value_ref)
            )


class TestStepParameters(KeywordCallParametersInline):
    formset = TestStepParameterFormset


@admin.register(TestStep)
class TestStepAdmin(KeywordCallAdmin):
    def get_inlines(self, request, obj):
        return [TestStepParameters]

    @admin.display(description='Sequenz')
    def keyword_doc(self, obj: TestStep):
        return open_link_in_modal(
            Sequence(obj.to_keyword.pk).get_docadmin_url(),
            obj.to_keyword.name
        )
