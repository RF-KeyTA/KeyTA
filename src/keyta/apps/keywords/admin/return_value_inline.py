from django.db.models import Q
from django.utils.translation import gettext as _

from keyta.admin.base_inline import TabularInlineWithDelete
from keyta.widgets import BaseSelect

from ..models import KeywordReturnValue, Keyword


class ReturnValueInline(TabularInlineWithDelete):
    model = KeywordReturnValue
    fields = ['kw_call_return_value']
    extra = 0
    max_num = 1

    def get_formset(self, request, obj=None, **kwargs):
        keyword: Keyword = obj
        formset = super().get_formset(request, obj, **kwargs)
        kw_call_return_value_field = formset.form.base_fields['kw_call_return_value']
        return_values = (
            kw_call_return_value_field.queryset
            .filter(keyword_call__in=keyword.calls.all())
            .exclude(Q(name__isnull=True) & Q(return_value__isnull=True))
        )
        kw_call_return_value_field.queryset = return_values

        if return_values.exists():
            kw_call_return_value_field.widget = BaseSelect(
                _('Rückgabewert auswählen')
            )
        else:
            if return_value := keyword.return_value.first():
                return_value.delete()

            kw_call_return_value_field.disabled = True
            kw_call_return_value_field.widget = BaseSelect(
                _('Keine Rückgabewerte aus den Schritten')
            )

        return formset
