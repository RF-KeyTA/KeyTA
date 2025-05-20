from itertools import groupby

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from keyta.apps.actions.models import Action
from keyta.apps.keywords.admin import StepsInline
from keyta.apps.keywords.forms import StepsForm
from keyta.apps.keywords.models import Keyword, KeywordCall
from keyta.apps.windows.models import Window
from keyta.forms import form_with_select
from keyta.widgets import quick_change_widget

from ..models import Sequence


def global_actions(systems: QuerySet):
    global_actions = (
        Action.objects
        .filter(systems__in=systems)
        .filter(windows__isnull=True)
        .filter(setup_teardown=False)
    )

    if not global_actions.exists():
        return []

    return [[
        _('Globale Aktionen'), [
            (action.pk, action.name)
            for action in global_actions
            .distinct()
        ]
    ]]


class SequenceSteps(StepsInline):
    model = KeywordCall
    form = form_with_select(
        KeywordCall,
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
                .filter(systems__in=sequence.systems.values_list('id', flat=True))
            ] or [(None, _('Keine Aktionen vorhanden'))]
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

        to_keyword_field = formset.form.base_fields['to_keyword']
        to_keyword_field.choices = (
                [(None, None)] +
                window_actions +
                resource_kws +
                global_actions(sequence.systems.all())
        )
        to_keyword_field.widget = quick_change_widget(to_keyword_field.widget)

        return formset
