from django import forms
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import TabularInlineWithDelete
from keyta.apps.windows.models import Window
from keyta.widgets import ModelSelect2AdminWidget

from ..models import Action, ActionWindowRelation


class Windows(TabularInlineWithDelete):
    model = ActionWindowRelation
    extra = 0
    fields = ['window']
    form = forms.modelform_factory(
        ActionWindowRelation,
        fields=['window'],
        labels={
            'window': _('Maske')
        },
        widgets={
            'window': ModelSelect2AdminWidget(
                placeholder=_('Maske auswählen'),
                model=Window,
                search_fields=['name__icontains'],
            )
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
        window_field.widget.can_add_related = False
        window_field.widget.can_change_related = False
        window_field.widget.can_view_related = False

        return formset

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None):
        return self.can_change(request.user, 'action')
