from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import TabularInlineWithDelete
from keyta.widgets import ModelSelect2AdminWidget

from ..models import KeywordReturnValue, Keyword


class ReturnValueInline(TabularInlineWithDelete):
    model = KeywordReturnValue
    fields = ['kw_call_return_value']
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        keyword: Keyword = obj
        formset = super().get_formset(request, obj, **kwargs)
        kw_call_return_value_field = formset.form.base_fields['kw_call_return_value']
        return_values = (
            kw_call_return_value_field.queryset
            .filter(keyword_call__in=keyword.calls.all())
        )
        kw_call_return_value_field.queryset = return_values
        kw_call_return_value_field.widget = ModelSelect2AdminWidget(
            model=KeywordReturnValue,
            placeholder=_('Rückgabewert auswählen'),
            search_fields=['name__icontains'],
        )

        return formset

    def has_add_permission(self, request, obj):
        keyword: Keyword = obj

        if keyword and keyword.in_use:
            return False

        super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        keyword: Keyword = obj

        if keyword and keyword.in_use:
            return False

        super().has_delete_permission(request, obj)
