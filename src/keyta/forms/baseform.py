from django import forms

from keyta.widgets import BaseSelect, BaseSelectMultiple


class BaseForm(forms.ModelForm):
    fields_can_add_related = []
    fields_can_change_related = []
    fields_can_view_related = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.can_add_related = field_name in self.fields_can_add_related
            field.widget.can_change_related = field_name in self.fields_can_change_related and self.initial
            field.widget.can_delete_related = False
            field.widget.can_view_related = field_name in self.fields_can_view_related and self.initial


def form_with_select(
        model,
        select_field: str,
        placeholder: str,
        labels=None,
        form_class=BaseForm,
        field_classes=None,
        select_many=False,
        can_add_related=False,
        can_change_related=False,
        can_view_related=False
):

    if select_many:
        SelectWidget = BaseSelectMultiple
    else:
        SelectWidget = BaseSelect

    form = forms.modelform_factory(
        model,
        form_class,
        [select_field],
        field_classes=field_classes,
        labels=labels,
        widgets={
            select_field: SelectWidget(placeholder)
        }
    )

    if can_add_related:
        form.fields_can_add_related = [select_field]

    if can_change_related:
        form.fields_can_change_related = [select_field]

    if can_view_related:
        form.fields_can_view_related = [select_field]

    return form
