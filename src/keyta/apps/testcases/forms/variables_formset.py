from django.urls import reverse
from nonrelated_inlines.forms import NonrelatedInlineFormSet

from keyta.apps.variables.models import VariableQuickAdd
from keyta.widgets import quick_change_widget, quick_add_widget


class VariablesFormset(NonrelatedInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        quick_add_field = form.fields[self.quick_add_field()]

        # The index of extra forms is None
        if index is None:
            app = self.quick_add_model()._meta.app_label
            model = self.quick_add_model()._meta.model_name
            quick_add_url = reverse('admin:%s_%s_add' % (app, model))

            quick_add_field.widget = quick_add_widget(
                quick_add_field.widget,
                quick_add_url,
                self.quick_add_url_params()
            )

        variable_field = form.fields['variable']

        # The index of extra forms is None
        if index is not None:
            variable_field.widget = quick_change_widget(variable_field.widget)
            variable_field.widget.attrs['disabled'] = 'disabled'

    def quick_add_field(self) -> str:
        return 'variable'

    def quick_add_model(self):
        return VariableQuickAdd

    def quick_add_url_params(self):
        window = self.instance.window
        system_pks = window.systems.values_list('pk', flat=True)

        return {
            'quick_add': '1',
            'systems': ','.join([str(pk) for pk in system_pks]),
            'windows': window.pk
        }
