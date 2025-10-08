from django import forms
from django.utils.translation import gettext_lazy as _

from keyta.apps.windows.models import Window
from keyta.forms import BaseForm

from ..models import Variable


class WindowsForm(BaseForm):
    def clean(self):
        window: Window = self.cleaned_data.get('window')
        variable: Variable = self.cleaned_data.get('variable')

        if window.variables.filter(name__iexact=variable.name).exists():
            raise forms.ValidationError(
                {
                    "window": _(f'Eine Variable mit diesem Namen existiert bereits in der Maske "{window.name}"')
                }
            )
