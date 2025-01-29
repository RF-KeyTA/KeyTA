from django.db.models import QuerySet, Q
from django.utils.translation import gettext as _

from keyta.admin.base_inline import TabularInlineWithDelete

from ..models import KeywordReturnValue, Keyword


class ReturnValueInline(TabularInlineWithDelete):
    model = KeywordReturnValue
    fields = ['kw_call_return_value']
    extra = 1
    max_num = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        keyword: Keyword = obj
        queryset: QuerySet = formset.form.base_fields['kw_call_return_value'].queryset
        return_values = (
            queryset
            .filter(keyword_call__in=keyword.calls.all())
            .exclude(Q(name__isnull=True) & Q(return_value__isnull=True))
        )
        formset.form.base_fields['kw_call_return_value'].queryset = return_values

        if return_values.exists():
            formset.form.base_fields['kw_call_return_value'].widget.attrs.update({
                'data-placeholder': _('Rückgabewert auswählen')
            })
        else:
            formset.form.base_fields['kw_call_return_value'].disabled = True
            formset.form.base_fields['kw_call_return_value'].empty_label = _('Keine Rückgabewerte aus den Schritten')

        return formset
