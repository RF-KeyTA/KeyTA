from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext as _

from keyta.admin.base_inline import TabularInlineWithDelete
from keyta.forms.baseform import form_with_select

from ..models.action import Action, ActionWindowRelation


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
        systems = action.systems.all()
        
        formset = super().get_formset(request, obj, **kwargs)
        windows_queryset: QuerySet = formset.form.base_fields['window'].queryset
        windows_queryset = windows_queryset.filter(systems__in=systems).distinct()

        return formset

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False
