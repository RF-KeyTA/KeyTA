from itertools import groupby

from adminsortable2.admin import CustomInlineFormSet

from django.db.models import QuerySet
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from keyta.apps.actions.models import Action
from keyta.apps.keywords.models import Keyword
from keyta.apps.windows.models import Window
from keyta.widgets import quick_change_widget, CustomRelatedFieldWidgetWrapper

from ..models import Sequence, SequenceStep


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
    def __init__(
        self, default_order_direction=None, default_order_field=None, **kwargs
    ):
        super().__init__(default_order_direction, default_order_field, **kwargs)
        self.sequence: Sequence = kwargs['instance']

    def add_fields(self, form, index):
        super().add_fields(form, index)

        sequence_step: SequenceStep = form.instance

        execute_field = form.fields['execute']
        to_keyword_field = form.fields['to_keyword']

        execute_field.label = mark_safe('<span title="%s">▶</span>' % _('Ausführen ab'))

        # The index of an extra form is None
        if index is None:
            to_keyword_field.widget = CustomRelatedFieldWidgetWrapper(
                to_keyword_field.widget,
                reverse('admin:actions_actionquickadd_add'),
                {
                    'systems': self.sequence.systems.first().pk,
                    'windows': self.sequence.windows.first().pk
                }
            )
            to_keyword_field.widget.can_add_related = True
            to_keyword_field.widget.can_change_related = False
            to_keyword_field.widget.attrs.update({
                'data-width': '95%',
            })
        else:
            to_keyword_field.widget = quick_change_widget(
                to_keyword_field.widget,
                url_params={
                    'kw_call_pk': sequence_step.pk,
                    'tab_name': sequence_step.get_tab_url().removeprefix('#')
                }
            )

        window: Window = self.sequence.windows.first()
        resource_ids = window.resource_imports.values_list('resource_id')
        resource_kws = Keyword.objects.filter(resource__in=resource_ids)
        systems = self.sequence.systems.all()

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

        to_keyword_field.choices = (
            [(None, None)] +
            window_actions +
            resource_kws +
            global_actions(self.sequence.systems.all())
        )
