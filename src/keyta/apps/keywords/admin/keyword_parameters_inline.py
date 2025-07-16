from django import forms
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import SortableTabularInlineWithDelete

from ..models import Keyword, KeywordParameter


class ParameterForm(forms.ModelForm):
    def clean_name(self):
        name = self.cleaned_data.get('name')

        if ':' in name:
            raise forms.ValidationError("Doppelpunkt ist im Parameternamen nicht zulässig")

        return name


class ParametersInline(SortableTabularInlineWithDelete):
    model = KeywordParameter
    fields = ['position', 'name']
    form = ParameterForm
    extra = 0
    verbose_name = _('Parameter')
    verbose_name_plural = _('Parameters')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'name':
            field.widget.attrs.update({'style': 'width: 100%'})

        return field

    def has_add_permission(self, request, obj):
        keyword: Keyword = obj

        if keyword and keyword.in_use:
            return False

        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        keyword: Keyword = obj

        if keyword and keyword.in_use:
            return False

        return super().has_delete_permission(request, obj)
