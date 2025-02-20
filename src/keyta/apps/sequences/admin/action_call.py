from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.apps.keywords.admin import KeywordCallAdmin

from ..models import ActionCall


@admin.register(ActionCall)
class ActionCallAdmin(KeywordCallAdmin):
    @admin.display(description=_('Aktion'))
    def to_keyword_doc(self, action_call: ActionCall):
        return super().to_keyword_doc(action_call)
