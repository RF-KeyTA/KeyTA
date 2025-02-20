from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseAdmin
from keyta.widgets import open_link_in_modal

from ..models import (
    KeywordCall,
    KeywordCallReturnValue
)
from .keywordcall_parameters_inline import KeywordCallParametersInline


@admin.register(KeywordCall)
class KeywordCallAdmin(BaseAdmin):
    fields = [
        'to_keyword_doc',
        'return_value'
    ]
    readonly_fields = [
        'to_keyword_doc',
        'return_value'
    ]
    inlines = [KeywordCallParametersInline]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        kw_call = KeywordCall.objects.get(pk=object_id)
        kw_call.update_parameter_values()

        return super().change_view(request, object_id, form_url, extra_context)

    def get_inlines(self, request, obj):
        kw_call: KeywordCall = obj

        if kw_call.parameters.exists():
            return self.inlines
        else:
            return []

    @admin.display(description=_('Rückgabewert'))
    def return_value(self, obj):
        kw_call: KeywordCall = obj
        return_value: KeywordCallReturnValue = kw_call.return_value.first()

        if return_value and return_value.is_set:
            return str(return_value)

        return _('Kein Rückgabewert')

    def to_keyword_doc(self, kw_call: KeywordCall):
        return open_link_in_modal(
            kw_call.to_keyword.get_docadmin_url(),
            kw_call.to_keyword.name
        )
