from django.contrib import admin

from keyta.apps.keywords.admin import ConditionsInline, KeywordCallAdmin

from ..models import SequenceStep


@admin.register(SequenceStep)
class SequenceStepAdmin(KeywordCallAdmin):
    def change_view(self, request, object_id, form_url="", extra_context=None):
        return self.changeform_view(request, object_id, form_url, extra_context or {'show_delete': False})

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)
        kw_call: SequenceStep = obj

        if kw_call.from_keyword.parameters.exists() or kw_call.get_previous_return_values().exists():
            for condition in kw_call.conditions.all():
                condition.update_expected_value()

            return inlines + [ConditionsInline]

        return inlines
