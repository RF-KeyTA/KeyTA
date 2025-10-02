from django.forms import BaseInlineFormSet

from keyta.widgets import quick_change_widget


class SetupTeardownFormset(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        to_keyword_field = form.fields['to_keyword']
        to_keyword_field.widget.can_change_related = True
        to_keyword_field.widget = quick_change_widget(
            to_keyword_field.widget
        )
