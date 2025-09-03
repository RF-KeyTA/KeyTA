from django import forms
from django.utils.translation import gettext as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.windows.models import WindowSystemRelation

from ..forms import WindowsFormset


class Windows(BaseTabularInline):
    model = WindowSystemRelation
    form = forms.modelform_factory(
        WindowSystemRelation,
        fields=['window'],
        labels={
            'window': _('Maske')
        }
    )
    formset = WindowsFormset
    verbose_name = _('Maske')
    verbose_name_plural = _('Masken')

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('window')
            .order_by('window__name')
        )

    def has_change_permission(self, request, obj=None):
        return False
