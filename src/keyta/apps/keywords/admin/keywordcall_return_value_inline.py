from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField

from ..models import KeywordCall, KeywordCallReturnValue


class ReturnValueTypeField:
    def get_fields(self, request, obj=None):
        kw_call: KeywordCall = obj
        fields = super().get_fields(request, obj=obj)

        return_value: KeywordCallReturnValue
        for return_value in kw_call.return_values.all():
            if return_value.type:
                return fields + ['type']

        return fields

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj) + ['type']

    @admin.display(description=_('Type'))
    def type(self, kw_call_return_value: KeywordCallReturnValue):
        if type_ := kw_call_return_value.type:
            return mark_safe(type_)

        return '-'


class KeywordCallReturnValueInline(DeleteRelatedField, ReturnValueTypeField, BaseTabularInline):
    model = KeywordCallReturnValue
    fields = ['name']
    extra = 0
    verbose_name = _('Rückgabewert')
    verbose_name_plural = _('Rückgabewerte')
    can_delete = False


class ReadOnlyReturnValuesInline(KeywordCallReturnValueInline):
    fields = ['return_value_name']
    readonly_fields = ['return_value_name']
    max_num = 0

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description=_('Name'))
    def return_value_name(self, return_value: KeywordCallReturnValue):
        return str(return_value)
