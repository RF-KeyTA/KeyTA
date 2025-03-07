from itertools import groupby

from django.utils.translation import gettext as _

from keyta.apps.actions.models import Action
from keyta.apps.keywords.admin import StepsInline
from keyta.apps.keywords.forms import StepsForm
from keyta.apps.keywords.models import Keyword
from keyta.forms import form_with_select

from apps.windows.models import Window

from ..models import ActionCall, Sequence


class SequenceSteps(StepsInline):
    model = ActionCall
    form = form_with_select(
        ActionCall,
        'to_keyword',
        _('Aktion auswählen'),
        labels={
            'to_keyword': _('Aktion')
        },
        form_class=StepsForm,
        can_change_related=True
    )

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        sequence: Sequence = obj
        window: Window = sequence.windows.first()

        resource_ids = window.resource_imports.values_list('resource_id')
        resource_kws = Keyword.objects.filter(resource__in=resource_ids)

        window_actions = [[
            window.name, [
                (action.pk, action.name)
                for action in Action.objects
                .filter(windows=window)
            ]
        ]]

        global_actions = [[
            _('Globale Aktionen'), [
                (action.pk, action.name)
                for action in Action.objects
                .filter(systems__in=sequence.systems.all())
                .filter(windows__isnull=True)
                .filter(setup_teardown=False)
                .distinct()
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
                resource_kws +
                global_actions
        )

        return formset
