from django import forms
from django.utils.translation import gettext_lazy as _

from keyta.apps.windows.models import Window
from keyta.forms import BaseForm

from ..models import Action


class WindowsForm(BaseForm):
    def clean(self):
        window: Window = self.cleaned_data.get('window')
        action: Action = self.cleaned_data.get('keyword')

        if window.actions.filter(name__iexact=action.name).exists():
            raise forms.ValidationError(
                {
                    "window": _(f'Eine Aktion mit diesem Namen existiert bereits in der Maske "{window.name}"')
                }
            )
