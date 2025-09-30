from django import forms
from django.utils.translation import gettext_lazy as _

from keyta.forms import BaseForm


class ActionForm(BaseForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        systems = self.cleaned_data.get('systems')
        action_systems = [
            system.name
            for system in self.initial.get('systems', [])
        ]

        if systems:
            if system := systems.values_list('name', flat=True).exclude(name__in=action_systems).filter(keywords__name__iexact=name).first():
                print(system)
                action = self._meta.model.objects.filter(name__iexact=name).filter(systems__name=system).filter(windows__isnull=True)
                if action.exists():
                    raise forms.ValidationError(
                        {
                            "name": _(f'Eine Aktion mit diesem Namen existiert bereits im System "{system}"')
                        }
                    )


class QuickAddActionForm(BaseForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        windows = self.cleaned_data.get('windows')

        if len(windows) == 1:
            window = windows[0]
            if window.actions.filter(name__iexact=name).exists():
                raise forms.ValidationError(
                    {
                        "name": _(f'Eine Aktion mit diesem Namen existiert bereits in der Maske "{window.name}"')
                    }
                )
