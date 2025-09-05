from keyta.admin.base_inline import TabularInlineWithDelete

from ..forms import KeywordCallConditionFormset
from ..models import KeywordCallCondition, KeywordCall


class ConditionsInline(TabularInlineWithDelete):
    model = KeywordCallCondition
    fields = ['value_ref', 'condition', 'expected_value']
    formset = KeywordCallConditionFormset

    def has_add_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        keywordcall: KeywordCall = obj

        if keywordcall and keywordcall.testcase:
            return self.can_change(request.user, 'testcase')

        if keywordcall and keywordcall.from_keyword:
            return self.can_change(request.user, 'action') or self.can_change(request.user, 'sequence')

        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)
