from django.utils.translation import gettext_lazy as _

from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.admin.base_inline import BaseTabularInline
from keyta.widgets import ModelSelect2AdminWidget

from ..models import Keyword, KeywordCallReturnValue, KeywordReturnValue


class ReturnValueInline(DeleteRelatedField, BaseTabularInline):
    model = KeywordReturnValue
    fields = ['kw_call_return_value']
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        keyword: Keyword = obj
        kw_call_return_value_ids = (
            self.get_queryset(request)
            .filter(keyword__id=keyword.pk)
            .values_list('kw_call_return_value_id', flat=True)
        )
        kw_call_return_value_field = formset.form.base_fields['kw_call_return_value']
        kw_call_return_value_field.queryset = (
            kw_call_return_value_field.queryset
            .filter(keyword_call__in=keyword.calls.all())
            .exclude(id__in=kw_call_return_value_ids)
        )
        kw_call_return_value_field.widget = ModelSelect2AdminWidget(
            model=KeywordReturnValue,
            placeholder=_('Rückgabewert auswählen'),
            search_fields=['name__icontains'],
        )

        return formset

    def get_max_num(self, request, obj=None, **kwargs):
        keyword: Keyword = obj
        return KeywordCallReturnValue.objects.filter(keyword_call__in=keyword.calls.all()).count()

    def has_change_permission(self, request, obj=None):
        return False
