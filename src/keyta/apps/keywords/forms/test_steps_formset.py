from adminsortable2.admin import CustomInlineFormSet

from keyta.apps.keywords.models import KeywordCall
from keyta.apps.testcases.models import TestCase
from keyta.widgets import CustomRelatedFieldWidgetWrapper, quick_change_widget, LabelWidget


class TestStepsFormset(CustomInlineFormSet):
    def __init__(
        self, default_order_direction=None, default_order_field=None, **kwargs
    ):
        super().__init__(default_order_direction, default_order_field, **kwargs)
        self.parent: TestCase = kwargs['instance']

    def add_fields(self, form, index):
        super().add_fields(form, index)

        test_step: KeywordCall = form.instance

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

        # The index of an extra form is None
        if index is not None and test_step.pk:
            if not test_step.to_keyword:
                form.fields['to_keyword'].widget.can_change_related = False

            if not test_step.variable:
                form.fields['variable'].widget.can_change_related = False

            if not test_step.parameters.exists():
                form.fields['variable'].widget = LabelWidget()

            form.fields['to_keyword'].widget = quick_change_widget(
                form.fields['to_keyword'].widget,
                url_params={'tab_name': test_step.get_tab_url().removeprefix('#')}
            )
            form.fields['to_keyword'].widget.can_add_related = False
            form.fields['to_keyword'].widget.can_change_related = True
