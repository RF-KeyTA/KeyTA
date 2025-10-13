from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.admin.base_inline import SortableTabularInline

from ..models import Keyword, KeywordParameter


class ParameterForm(forms.ModelForm):
    def clean_name(self):
        name = self.cleaned_data.get('name')

        if ':' in name:
            raise forms.ValidationError("Doppelpunkt ist im Parameternamen nicht zulässig")

        return name


class ParametersInline(DeleteRelatedField, SortableTabularInline):
    model = KeywordParameter
    fields = ['position', 'name']
    form = ParameterForm
    extra = 0
    verbose_name = _('Parameter')
    verbose_name_plural = _('Parameters')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'name':
            field.widget = forms.TextInput(attrs={
                'style': 'width: 100%',
                'placeholder': _('Name eintragen, anschließend Tab drücken')
            })

        return field

    def get_max_num(self, request, obj=None, **kwargs):
        keyword: Keyword = obj

        if keyword and keyword.uses.exclude(Q(execution__isnull=False) & Q(to_keyword=keyword)).count() > 1:
            return keyword.parameters.count()

        return super().get_max_num(request, obj=obj, **kwargs)

    def has_delete_permission(self, request, obj=None):
        keyword: Keyword = obj

        if keyword and keyword.is_action:
            return self.can_change(request.user, 'action')

        if keyword and keyword.is_sequence:
            return self.can_change(request.user, 'sequence')

        return super().has_delete_permission(request, obj)
