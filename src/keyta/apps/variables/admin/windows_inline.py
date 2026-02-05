from django import forms
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import TabularInlineWithDelete
from keyta.apps.windows.models import Window
from keyta.widgets import ModelSelect2AdminWidget

from ..forms import WindowsForm
from ..models import Variable, VariableWindowRelation


class Windows(TabularInlineWithDelete):
    model = VariableWindowRelation
    extra = 0
    fields = ['window']
    form = forms.modelform_factory(
        VariableWindowRelation,
        form=WindowsForm,
        fields=['window'],
        labels={
            'window': _('Maske')
        },
        widgets={
            'window': ModelSelect2AdminWidget(
                placeholder=_('Maske auswählen'),
                model=Window,
                search_fields=['name__icontains']
            )
        }
    )
    tab_name = _('Masken').lower()
    verbose_name = _('Maske')
    verbose_name_plural = _('Masken')

    def get_formset(self, request, obj=None, **kwargs):
        variable: Variable = obj
        formset = super().get_formset(request, obj, **kwargs)
        window_field = formset.form.base_fields['window']

        if variable:
            window_field.queryset = (
                window_field.queryset
                .exclude(id__in=variable.windows.values_list('id', flat=True))
                .filter(systems__in=variable.systems.all())
                .distinct()
            )

        return formset

    def has_change_permission(self, request, obj=None) -> bool:
        return False
