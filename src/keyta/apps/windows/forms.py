from django import forms
from django.utils.translation import gettext_lazy as _

from keyta.forms import BaseForm


class WindowForm(BaseForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        systems = self.cleaned_data.get('systems')
        window_systems = [
            system.name
            for system in self.initial.get('systems', [])
        ]

        if systems:
            if system := systems.exclude(name__in=window_systems).filter(windows__name=name).first():
                raise forms.ValidationError(
                    {
                        "name": _(f'Eine Maske mit diesem Namen existiert bereits im System "{system}"')
                    }
                )
