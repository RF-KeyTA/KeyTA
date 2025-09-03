from django import forms
from django.urls import reverse

from keyta.apps.windows.models import WindowQuickAdd
from keyta.widgets import quick_add_widget

from ..models import System


class WindowsFormset(forms.BaseInlineFormSet):
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
        self.system: System = instance

    def add_fields(self, form, index):
        super().add_fields(form, index)

        window_field = form.fields['window']

        # The index of extra forms is None
        if index is None:
            app = WindowQuickAdd._meta.app_label
            model = WindowQuickAdd._meta.model_name
            quick_add_url = reverse('admin:%s_%s_add' % (app, model))

            window_field.widget = quick_add_widget(
                window_field.widget,
                quick_add_url,
                {
                    'quick_add': '1',
                    'systems': str(self.system.pk)
                }
            )
