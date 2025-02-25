from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseAdmin
from keyta.apps.keywords.models import KeywordDocumentation
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

    def change_view(self, request, object_id, form_url="", extra_context=None):
        kw_call = KeywordCall.objects.get(pk=object_id)
        kw_call.update_parameters()
        kw_call.update_parameter_values()
        kw_call.update_return_value()

        return super().change_view(request, object_id, form_url, extra_context)

    def get_inlines(self, request, obj):
        kw_call: KeywordCall = obj

        if kw_call.parameters.exists():
            return [KeywordCallParametersInline] + self.inlines
        else:
            return self.inlines

    @admin.display(description=_('Rückgabewert'))
    def return_value(self, obj):
        kw_call: KeywordCall = obj
        return_value: KeywordCallReturnValue = kw_call.return_value.first()

        if return_value and return_value.is_set:
            return str(return_value)

        return _('Kein Rückgabewert')

    def to_keyword_doc(self, kw_call: KeywordCall):
        keyword_doc = KeywordDocumentation(kw_call.to_keyword.pk)

        return open_link_in_modal(
            keyword_doc.get_admin_url(),
            kw_call.to_keyword.name
        )
