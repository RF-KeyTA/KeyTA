from django import forms
from django.utils.translation import gettext_lazy as _

from keyta.widgets import quick_change_widget

from ..models import Window


class QuickChangeTemplateVariablesFormset(forms.BaseInlineFormSet):
    def __init__(
        self,
        data=None,
        files=None,
        instance=None,
        save_as_new=False,
        prefix=None,
        queryset=None,
        **kwargs,
    ):
        super().__init__(data, files, instance, save_as_new, prefix, queryset, **kwargs)

        self.window: Window = instance

    def add_fields(self, form, index):
        super().add_fields(form, index)

        variable_field = form.fields['variable']

        # The index of extra forms is None
        if index is None:
            variable_field.widget.attrs.update({
                'data-placeholder': _('Referenzwert auswählen'),
            })
        else:
            variable_field.widget = quick_change_widget(variable_field.widget)

        # Set the queryset after replacing the widget
        variable_field.queryset = variable_field.queryset.exclude(template='')
