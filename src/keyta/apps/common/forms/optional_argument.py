from django import forms

from apps.common.widgets import BaseSelect


class OptionalArgumentFormSet(forms.BaseInlineFormSet):
    value_field = 'value'

    def add_fields(self, form, index):
        super().add_fields(form, index)

        kwarg = form.instance

        if getattr(kwarg, self.value_field) in {"True", "False"}:
            form.fields[self.value_field].widget = BaseSelect(
                'Wert auswählen',
                choices=[("True", "True"), ("False", "False")],
            )

        form.fields[self.value_field].widget.attrs.update({'style': 'width:100%'})
