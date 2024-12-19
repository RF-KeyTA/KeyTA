from itertools import groupby

from django.utils.translation import gettext as _

from apps.actions.models import Action
from apps.common.widgets import BaseSelect
from apps.keywords.admin import StepsInline
from apps.keywords.models import Keyword
from apps.windows.models import Window

from ..models import ActionCall, Sequence


class SequenceSteps(StepsInline):
    model = ActionCall
    fk_name = 'from_keyword'

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        sequence: Sequence = obj
        window: Window = sequence.windows.first()

        resource_kws = Keyword.objects.filter(resource__in=sequence.resource_ids)

        window_actions = [[
            window.name, [
                (action.pk, action.name)
                for action in Action.objects
                .filter(windows=window)
                .order_by('name')
            ]
        ]]

        global_actions = [[
            _('Globale Aktionen'), [
                (action.pk, action.name)
                for action in Action.objects
                .filter(everywhere=True)
                .filter(systems__in=sequence.systems.all())
                .distinct()
                .order_by('name')
            ]
        ]]

        groups = groupby(resource_kws, key=lambda x: getattr(x, 'resource'))
        resource_kws = [
            [
                resource.name, [
                    (keyword.id, keyword.name)
                    for keyword in keywords
                ]
            ]
            for resource, keywords in groups
        ]

        field = formset.form.base_fields['to_keyword']
        field.choices = (
                [(None, None)] +
                window_actions +
                global_actions +
                resource_kws
        )
        field.label = _('Aktion')
        field.widget = BaseSelect(_('Aktion auswählen'))

        return formset
