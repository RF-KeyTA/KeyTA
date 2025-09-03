from django import forms
from django.urls import reverse

from keyta.widgets import quick_add_widget

from ..models import Window


class QuickAddFormset(forms.BaseInlineFormSet):
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

        quick_add_field = form.fields[self.quick_add_field()]

        # The index of extra forms is None
        if index is None:
            app = self.quick_add_model()._meta.app_label
            model = self.quick_add_model()._meta.model_name
            quick_add_url = reverse('admin:%s_%s_add' % (app, model))

            quick_add_field.widget = quick_add_widget(
                quick_add_field.widget,
                quick_add_url,
                {
                    'quick_add': '1',
                    'systems': ','.join([str(pk) for pk in self.system_pks]),
                    'windows': self.window.pk
                }
            )

    def quick_add_field(self) -> str:
        pass

    def quick_add_model(self):
        pass
