from django import forms
from django.urls import reverse

from keyta.apps.variables.models import VariableQuickAdd
from keyta.widgets import quick_add_widget, quick_change_widget, BaseSelect

from ..models import Window


class VariablesFormset(forms.BaseInlineFormSet):
    def __init__(
        self,
        data=None,
        files=None,
        instance=None,
        save_as_new=False,
        prefix=None,
        queryset=None,
        **kwargs
    ):
        super().__init__(data, files, instance, save_as_new, prefix, queryset, **kwargs)
        self.window: Window = instance
        self.system_pks = self.window.systems.values_list('pk', flat=True)

    def add_fields(self, form, index):
        super().add_fields(form, index)

        variable_field = form.fields['variable']

        # The index of extra forms is None
        if index is None:
            app = VariableQuickAdd._meta.app_label
            model = VariableQuickAdd._meta.model_name
            quick_add_url = reverse('admin:%s_%s_add' % (app, model))

            variable_field.widget = quick_add_widget(
                variable_field.widget,
                quick_add_url,
                {
                    'quick_add': '1',
                    'systems': ','.join([str(pk) for pk in self.system_pks]),
                    'windows': self.window.pk
                }
            )
        else:
            variable_field.widget = quick_change_widget(variable_field.widget)
            variable_field.widget.widget = BaseSelect(
                '',
                attrs={'disabled': 'true'}
            )
