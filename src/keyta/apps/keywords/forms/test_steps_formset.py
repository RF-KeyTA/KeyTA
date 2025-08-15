from django.urls import reverse

from adminsortable2.admin import CustomInlineFormSet

from keyta.apps.keywords.models import KeywordCall
from keyta.apps.testcases.models import TestCase
from keyta.widgets import (
    CustomRelatedFieldWidgetWrapper,
    LabelWidget,
    quick_change_widget
)


class TestStepsFormset(CustomInlineFormSet):
    def __init__(
        self, default_order_direction=None, default_order_field=None, **kwargs
    ):
        super().__init__(default_order_direction, default_order_field, **kwargs)
        self.parent: TestCase = kwargs['instance']

    def add_fields(self, form, index):
        super().add_fields(form, index)

        test_step: KeywordCall = form.instance

        # The index of extra forms is None
        if index is None:
            window_field = form.fields['window']
            window_field.widget = CustomRelatedFieldWidgetWrapper(
                window_field.widget,
                None,
                {'systems': self.parent.systems.first().pk}
            )
            window_field.widget.can_add_related = True
            window_field.widget.attrs.update({
                'data-width': '95%',
            })
        else:
            if test_step.pk:
                if not test_step.to_keyword:
                    to_keyword_field = form.fields['to_keyword']
                    to_keyword_field.widget.can_change_related = False
                    to_keyword_field.widget = CustomRelatedFieldWidgetWrapper(
                        to_keyword_field.widget,
                        reverse('admin:sequences_sequence_add'),
                        {
                            'systems': self.parent.systems.first().pk,
                            'windows': test_step.window.pk
                        }
                    )
                    to_keyword_field.widget.can_add_related = True
                    to_keyword_field.widget.attrs.update({
                        'data-width': '95%',
                    })
                else:
                    to_keyword_field = form.fields['to_keyword']
                    to_keyword_field.widget = quick_change_widget(
                        to_keyword_field.widget,
                        url_params={'tab_name': test_step.get_tab_url().removeprefix('#')}
                    )
                    to_keyword_field.widget.can_add_related = False
                    to_keyword_field.widget.can_change_related = True

                if not test_step.variable:
                    form.fields['variable'].widget.can_change_related = False

                if not test_step.parameters.exists():
                    form.fields['variable'].widget = LabelWidget()
