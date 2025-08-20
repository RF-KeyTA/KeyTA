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

    def get_windows(self, request, obj):
        action: Action = obj

        return (
            self.get_queryset(request)
            .filter(keyword_id=action.pk)
            .values_list('window_id', flat=True)
        )

    def get_systems(self, obj):
        action: Action = obj

        return action.systems.all()

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        window_field = formset.form.base_fields['window']
        window_field.queryset = (
            window_field.queryset
            .exclude(id__in=self.get_windows(request, obj))
            .filter(systems__in=self.get_systems(obj))
            .distinct()
        )

        return formset

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False
