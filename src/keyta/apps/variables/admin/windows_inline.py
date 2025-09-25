from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import TabularInlineWithDelete
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
