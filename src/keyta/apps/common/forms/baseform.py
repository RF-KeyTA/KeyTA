from django import forms

from apps.common.widgets import BaseSelect, BaseSelectMultiple


class BaseForm(forms.ModelForm):
    fields_can_view_related = []

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
            field.widget.can_view_related = field_name in self.fields_can_view_related


def form_with_select(
        model,
        select_field: str,
        placeholder: str,
        labels=None,
        select_many=False,
        can_view_related=False
):

    if select_many:
        SelectWidget = BaseSelectMultiple
    else:
        SelectWidget = BaseSelect

    form = forms.modelform_factory(
        model,
        BaseForm,
        [select_field],
        labels=labels,
        widgets={
            select_field: SelectWidget(placeholder)
        }
    )

    if can_view_related:
        form.fields_can_view_related = [select_field]

    return form
