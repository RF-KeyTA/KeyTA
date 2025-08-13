from itertools import groupby

from adminsortable2.admin import CustomInlineFormSet

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
    ).distinct()

    if not global_actions.exists():
        return []

    return [[
        _('Globale Aktionen'), [
            (action.pk, action.name)
            for action in global_actions
            .distinct()
        ]
    ]]


class SequenceStepsFormset(CustomInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        sequence_step: KeywordCall = form.instance

        # The index of an extra form is None
        if index is not None and sequence_step.pk:
            if not sequence_step.to_keyword:
                form.fields['to_keyword'].widget.can_change_related = False

            form.fields['to_keyword'].widget = quick_change_widget(
                form.fields['to_keyword'].widget,
                url_params={'tab_name': sequence_step.get_tab_url().removeprefix('#')}
            )
            form.fields['to_keyword'].widget.can_add_related = False
            form.fields['to_keyword'].widget.can_change_related = True


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
    formset = SequenceStepsFormset

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        sequence: Sequence = obj
        window: Window = sequence.windows.first()
        resource_ids = window.resource_imports.values_list('resource_id')
        resource_kws = Keyword.objects.filter(resource__in=resource_ids)
        systems = sequence.systems.all()

        window_actions = [[
            window.name, [
                (action.pk, action.name)
                for action in Action.objects
                .filter(windows=window)
                .filter(systems__in=systems)
                .distinct()
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

        return formset
