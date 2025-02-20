from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.apps.keywords.admin import (
    KeywordCallAdmin,
    KeywordCallReturnValueInline
)

from ..models import RobotKeywordCall


@admin.register(RobotKeywordCall)
class RobotKeywordCallAdmin(KeywordCallAdmin):
    fields = ['to_keyword_doc']
    readonly_fields = ['to_keyword_doc']
    inlines = [KeywordCallReturnValueInline]

    @admin.display(description=_('Schlüsselwort'))
    def to_keyword_doc(self, kw_call: RobotKeywordCall):
        return super().to_keyword_doc(kw_call)
