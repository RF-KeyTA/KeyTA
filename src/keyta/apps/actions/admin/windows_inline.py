from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import TabularInlineWithDelete
from keyta.forms.baseform import form_with_select

from ..models import Action, ActionWindowRelation


class Windows(TabularInlineWithDelete):
    model = ActionWindowRelation
    extra = 0
    fields = ['window']
    form = form_with_select(
        ActionWindowRelation,
        'window',
        _('Maske auswählen'),
        labels={
            'window': _('Maske')
        }
    )
    verbose_name = _('Maske')
    verbose_name_plural = _('Masken')

    def get_formset(self, request, obj=None, **kwargs):
        action: Action = obj
        formset = super().get_formset(request, obj, **kwargs)
        window_field = formset.form.base_fields['window']
        window_field.queryset = (
            window_field.queryset
            .exclude(id__in=action.windows.values_list('id', flat=True))
            .filter(systems__in=action.systems.all())
            .distinct()
        )

        return formset

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None):
        return self.can_change(request.user, 'action')
