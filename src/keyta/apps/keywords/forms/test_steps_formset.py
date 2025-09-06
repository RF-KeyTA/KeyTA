from django.urls import reverse

from adminsortable2.admin import CustomInlineFormSet

from keyta.apps.resources.models import ResourceImport
from keyta.apps.testcases.models import TestCase
from keyta.apps.windows.models import Window
from keyta.widgets import (
    CustomRelatedFieldWidgetWrapper,
    LabelWidget,
    quick_change_widget
)

from ..models import Keyword, KeywordCall


class TestStepsFormset(CustomInlineFormSet):
    def __init__(
        self, default_order_direction=None, default_order_field=None, **kwargs
    ):
        super().__init__(default_order_direction, default_order_field, **kwargs)
        self.testcase: TestCase = kwargs['instance']
        # Perform all DB queries once when the formset is initialized
        self.system_pks = list(self.testcase.systems.values_list('pk', flat=True))
        self.windows = (
            Window.objects
            .filter(systems__in=self.system_pks)
            .distinct()
        )
        self.resource_ids = (
            ResourceImport.objects
            .filter(window__in=self.windows)
            .values_list('resource')
            .distinct()
        )
        self.to_keyword = (
            Keyword.objects.sequences().filter(systems__in=self.system_pks) |
            Keyword.objects.filter(resource__in=self.resource_ids)
        ).distinct().order_by('name')

    def add_fields(self, form, index):
        super().add_fields(form, index)

        test_step: KeywordCall = form.instance

        execute_field = form.fields['execute']
        to_keyword_field = form.fields['to_keyword']
        # variable_field = form.fields['variable']
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
            window_field.widget = quick_change_widget(window_field.widget)

            if test_step.pk:
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
                        'data-width': '95%',
                    })
                else:
                    to_keyword_field.widget = quick_change_widget(
                        to_keyword_field.widget,
                        url_params={'tab_name': test_step.get_tab_url().removeprefix('#')}
                    )
                    to_keyword_field.widget.attrs.update({
                        'data-allow-clear': 'true'
                    })

                # if not test_step.variable:
                #     variable_field.widget.can_change_related = False
                # else:
                #     variable_field.widget = quick_change_widget(variable_field.widget)
                #
                # if not test_step.parameters.exists():
                #     variable_field.widget = LabelWidget()

        # Set the querysets after replacing the widgets
        to_keyword_field.queryset = self.to_keyword
        # variable_field.queryset = (
        #     variable_field.queryset
        #     .filter(systems__in=self.systems)
        # ).distinct().order_by('name')
        window_field.queryset = self.windows
