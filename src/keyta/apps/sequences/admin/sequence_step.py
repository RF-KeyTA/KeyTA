from django.contrib import admin

from keyta.apps.keywords.admin import KeywordCallAdmin

from ..models import SequenceStep


@admin.register(SequenceStep)
class SequenceStepAdmin(KeywordCallAdmin):
    def change_view(self, request, object_id, form_url="", extra_context=None):
        return self.changeform_view(request, object_id, form_url, extra_context or {'show_delete': False})
