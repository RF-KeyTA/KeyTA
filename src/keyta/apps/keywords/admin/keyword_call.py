from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseAdmin
from keyta.widgets import open_link_in_modal

from ..models import (
    KeywordCall,
    KeywordCallReturnValue,
    KeywordCallType,
    KeywordReturnValue
)
from .keywordcall_parameters_inline import KeywordCallParametersInline


class KeywordCallReturnValueInline(admin.TabularInline):
    model = KeywordCallReturnValue
    fields = ['name']
    extra = 1
    max_num = 1
    verbose_name = _('Rückgabewert')
    verbose_name_plural = _('Rückgabewert')
    can_delete = False


@admin.register(KeywordCall)
class KeywordCallAdmin(BaseAdmin):
    fields = [
        'keyword_doc',
        'return_value'
    ]
    readonly_fields = [
        'keyword_doc',
        'return_value'
    ]
    inlines = [KeywordCallParametersInline]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        kw_call = KeywordCall.objects.get(pk=object_id)

        if kw_call.type in [
            KeywordCallType.KEYWORD_CALL, KeywordCallType.TEST_STEP
        ]:
            if not kw_call.parameters.exists():
                for param in kw_call.to_keyword.parameters.all():
                    kw_call.add_parameter(param)

            if not kw_call.return_value.exists():
                return_value: KeywordReturnValue
                return_value = kw_call.to_keyword.return_value.first()

                if return_value:
                    KeywordCallReturnValue.objects.create(
                        keyword_call=kw_call,
                        return_value=return_value.kw_call_return_value
                    )

        return super().change_view(request, object_id, form_url, extra_context)


    def get_inlines(self, request, obj):
        kw_call: KeywordCall = obj

        if kw_call.parameters.exists():
            return self.inlines
        else:
            return []

    @admin.display(description=_('Dokumentation'))
    def keyword_doc(self, obj: KeywordCall):
        return open_link_in_modal(
            obj.to_keyword.get_docadmin_url(),
            obj.to_keyword.name
        )

    @admin.display(description=_('Rückgabewert'))
    def return_value(self, obj):
        kw_call: KeywordCall = obj
        return_value: KeywordCallReturnValue = kw_call.return_value.first()

        if return_value and return_value.is_set:
            return str(return_value)

        return _('Kein Rückgabewert')
