from django.contrib import admin
from django.utils.translation import gettext as _

from ..models import RobotKeywordCall
from .keywordcall import KeywordCallAdmin
from .keywordcall_return_value_inline import KeywordCallReturnValueInline


@admin.register(RobotKeywordCall)
class RobotKeywordCallAdmin(KeywordCallAdmin):
    fields = ['to_keyword_doc', 'condition']
    readonly_fields = ['to_keyword_doc']
    inlines = [KeywordCallReturnValueInline]

    @admin.display(description=_('Schlüsselwort'))
    def to_keyword_doc(self, kw_call: RobotKeywordCall):
        return super().to_keyword_doc(kw_call)
