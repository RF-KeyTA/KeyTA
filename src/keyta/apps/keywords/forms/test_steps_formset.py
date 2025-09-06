from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.urls import reverse

from adminsortable2.admin import CustomInlineFormSet

from keyta.apps.resources.models import ResourceImport
from keyta.apps.testcases.models import TestCase
from keyta.apps.windows.models import Window
from keyta.widgets import (
    CustomRelatedFieldWidgetWrapper,
    ModelSelect2AdminWidget
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
            .only('pk', 'name')
            .distinct()
        )
        self.resource_ids = (
            ResourceImport.objects
            .filter(window__in=self.windows)
            .values_list('resource')
            .distinct()
        )
        self.to_keyword = (
            (
            Keyword.objects.sequences().filter(systems__in=self.system_pks) |
            Keyword.objects.filter(resource__in=self.resource_ids)
            )
            .only('pk', 'name')
            .distinct()
            .order_by('name')
        )

        window_widget = ModelSelect2AdminWidget(
            placeholder='Maske auswählen',
            model=Window,
            queryset=self.windows,
            search_fields=['name__icontains'],
        )
        window_field = self.form.base_fields['window']
        window_field.widget = RelatedFieldWidgetWrapper(
            window_widget,
            window_field.widget.rel,
            window_field.widget.admin_site
        )

        to_keyword_widget = ModelSelect2AdminWidget(
            placeholder='Sequenz auswählen',
            model=Keyword,
            queryset=self.to_keyword,
            search_fields=['name__icontains'],
            dependent_fields={'window': 'windows'},
        )
        to_keyword_field = self.form.base_fields['to_keyword']
        to_keyword_field.widget = RelatedFieldWidgetWrapper(
            to_keyword_widget,
            to_keyword_field.widget.rel,
            to_keyword_field.widget.admin_site
        )

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
