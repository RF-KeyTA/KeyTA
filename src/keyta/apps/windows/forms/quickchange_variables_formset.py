from keyta.apps.variables.models import VariableQuickAdd
from keyta.widgets import quick_change_widget

from .quickadd_formset import QuickAddFormset


class QuickChangeVariablesFormset(QuickAddFormset):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        variable_field = form.fields['variable']

        # The index of extra forms is None
        if index is not None:
            variable_field.widget = quick_change_widget(variable_field.widget)
            variable_field.widget.attrs['disabled'] = 'disabled'

    def quick_add_field(self) -> str:
        return 'variable'

    def quick_add_model(self):
        return VariableQuickAdd
