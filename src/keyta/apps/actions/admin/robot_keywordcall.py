from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.widgets import open_link_in_modal
from apps.keywords.admin import (
    KeywordCallAdmin,
    KeywordCallParametersInline,
    KeywordCallReturnValueInline
)
from apps.keywords.forms import KeywordCallParameterFormset
from apps.keywords.models import Keyword, KeywordCall

from ..models.robot_keywordcall import RobotKeywordCall


class RobotKeywordCallParameterFormset(KeywordCallParameterFormset):
    def get_choices(self, obj):
        kw_call: KeywordCall = obj
        system_ids = list(
            kw_call.from_keyword.systems.values_list('pk', flat=True)
        )
        window_ids = list(
            kw_call.from_keyword.windows.values_list('pk', flat=True)
        )

        return super().get_choices(obj) + super().get_variables(
                window_ids,
                system_ids,
                lambda value_ref: str(value_ref)
            )


class RobotKeywordCallParameters(KeywordCallParametersInline):
    formset = RobotKeywordCallParameterFormset


@admin.register(RobotKeywordCall)
class RobotKeywordCallAdmin(KeywordCallAdmin):
    fields = ['keyword_doc']
    readonly_fields = ['keyword_doc']

    def get_inlines(self, request, obj):
        return [
            RobotKeywordCallParameters,
            KeywordCallReturnValueInline
        ]

    @admin.display(description=_('Schlüsselwort'))
    def keyword_doc(self, obj: RobotKeywordCall):
        return open_link_in_modal(
            Keyword(obj.to_keyword.pk).get_docadmin_url(),
            obj.to_keyword.name
        )
