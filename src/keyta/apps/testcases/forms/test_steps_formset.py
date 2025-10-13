from django.urls import reverse

from adminsortable2.admin import CustomInlineFormSet

from keyta.widgets import (
    CustomRelatedFieldWidgetWrapper,
    quick_change_widget
)

from ..models import TestCase, TestStep


class TestStepsFormset(CustomInlineFormSet):
    def __init__(
        self, default_order_direction=None, default_order_field=None, **kwargs
    ):
        super().__init__(default_order_direction, default_order_field, **kwargs)

        self.testcase: TestCase = kwargs['instance']
        # Perform all DB queries once when the formset is initialized
        self.system_pks = list(self.testcase.systems.values_list('pk', flat=True))

    def add_fields(self, form, index):
        super().add_fields(form, index)

        execute_field = form.fields['execute']
        to_keyword_field = form.fields['to_keyword']
        window_field = form.fields['window']

        # The index of extra forms is None
        if index is None:
            execute_field.widget.attrs.update({'disabled': 'disabled'})
            window_field.widget = CustomRelatedFieldWidgetWrapper(
                window_field.widget,
                None,
                {'systems': self.system_pks[0]}
            )
            window_field.widget.can_add_related = True
            window_field.widget.attrs.update({
                'data-width': '95%',
            })
        else:
            if form.instance.pk:
                test_step = TestStep.objects.get(pk=form.instance.pk)

                if not test_step.to_keyword:
                    to_keyword_field.widget.can_change_related = False
                    to_keyword_field.widget = CustomRelatedFieldWidgetWrapper(
                        to_keyword_field.widget,
                        reverse('admin:sequences_sequencequickadd_add'),
                        {
                            'systems': self.system_pks[0],
                            'windows': test_step.window.pk
                        }
                    )
                    to_keyword_field.widget.can_add_related = True
                    to_keyword_field.widget.attrs.update({
                        'data-width': '96.5%',
                        'data-style': 'width: 96.5%',
                    })
                else:
                    to_keyword_field.widget = quick_change_widget(
                        to_keyword_field.widget,
                        url_params={
                            'kw_call_pk': test_step.pk
                        }
                    )

                window_field.widget.can_change_related = True
