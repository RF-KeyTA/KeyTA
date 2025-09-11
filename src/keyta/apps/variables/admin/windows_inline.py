from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import TabularInlineWithDelete
from keyta.apps.windows.models import Window
from keyta.forms import form_with_select

from ..models import Variable, VariableWindowRelation


class Windows(TabularInlineWithDelete):
    model = VariableWindowRelation
    extra = 0
    fields = ['window']
    tab_name = _('Masken').lower()
    verbose_name = _('Maske')
    verbose_name_plural = _('Masken')

    form = form_with_select(
        VariableWindowRelation,
        'window',
        _('Maske auswählen'),
        labels={
            'window': _('Maske')
        }
    )

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        variable: Variable = obj

        if variable:
            systems = variable.systems.all()
            windows = Window.objects.filter(systems__in=systems).distinct()
            formset.form.base_fields['window'].queryset = windows

        return formset

    def has_change_permission(self, request, obj=None) -> bool:
        return False
