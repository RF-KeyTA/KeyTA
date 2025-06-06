from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

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
        formset = super().get_formset(request, obj, **kwargs)
        action: Action = obj
        systems = action.systems.all()
        windows = (
            self.get_queryset(request)
            .filter(keyword_id=action.pk)
            .values_list('window_id', flat=True)
        )

        window_field = formset.form.base_fields['window']
        window_field.queryset = (
            window_field.queryset
            .exclude(id__in=windows)
            .filter(systems__in=systems)
            .distinct()
        )

        return formset

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False
