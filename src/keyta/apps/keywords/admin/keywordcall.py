from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_admin import BaseAdmin
from keyta.apps.keywords.models import KeywordDocumentation
from keyta.widgets import open_link_in_modal

from ..models import (
    KeywordCall,
    KeywordCallReturnValue
)
from .keywordcall_parameters_inline import KeywordCallParametersInline
from .keywordcall_return_value_inline import KeywordCallReturnValueInline


class KeywordDocField:
    @admin.display(description=_(message='Dokumentation'))
    def to_keyword_doc(self, kw_call: KeywordCall):
        keyword_doc = KeywordDocumentation(kw_call.to_keyword.pk)

        return open_link_in_modal(
            keyword_doc.get_admin_url(),
            kw_call.to_keyword.name
        )

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj) + ['to_keyword_doc']

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj) + ['to_keyword_doc']


class ReturnValueField:
    @admin.display(description=_('Rückgabewert'))
    def return_value(self, obj):
        kw_call: KeywordCall = obj
        return_value: KeywordCallReturnValue = kw_call.return_value.first()

        if return_value and return_value.is_set:
            return str(return_value)

        return _('Kein Rückgabewert')
    
    def get_fields(self, request, obj=None):
        kw_call: KeywordCall = obj

        if not any([kw_call.to_keyword.library, kw_call.to_keyword.resource]):
            return super().get_fields(request, obj) + ['return_value']

        return super().get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        kw_call: KeywordCall = obj

        if not any([kw_call.to_keyword.library, kw_call.to_keyword.resource]):
            return super().get_readonly_fields(request, obj) + ['return_value']

        return super().get_readonly_fields(request, obj)


@admin.register(KeywordCall)
class KeywordCallAdmin(BaseAdmin):
    parameters_inline = KeywordCallParametersInline

    def change_view(self, request, object_id, form_url="", extra_context=None):
        kw_call = KeywordCall.objects.get(pk=object_id)
        kw_call.update_parameter_values()

        return super().change_view(request, object_id, form_url, extra_context)

    def get_fields(self, request, obj=None):
        return []

    def get_inlines(self, request, obj):
        kw_call: KeywordCall = obj

        inlines = []

        if kw_call.parameters.exists():
            inlines.append(self.parameters_inline)
        
        if kw_call.to_keyword.resource or kw_call.to_keyword.library:
            inlines.append(KeywordCallReturnValueInline)

        return inlines
