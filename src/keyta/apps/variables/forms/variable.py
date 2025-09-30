from django import forms
from django.utils.translation import gettext_lazy as _

from keyta.forms import BaseForm


class VariableForm(BaseForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        systems = self.cleaned_data.get('systems')
        variable_systems = [
            system.name
            for system in self.initial.get('systems', [])
        ]

        if systems:
            if system := systems.values_list('name', flat=True).exclude(name__in=variable_systems).filter(variables__name__iexact=name).first():
                variable = self._meta.model.objects.filter(name__iexact=name).filter(systems__name=system).filter(windows__isnull=True)
                if variable.exists():
                    raise forms.ValidationError(
                        {
                            "name": _(f'Eine Variable mit diesem Namen existiert bereits im System "{system}"')
                        }
                    )


class VariableQuickAddForm(BaseForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        windows = self.cleaned_data.get('windows')

        if len(windows) == 1:
            window = windows[0]
            if window.variables.filter(name__iexact=name).exists():
                raise forms.ValidationError(
                    {
                        "name": _(f'Eine Variable mit diesem Namen existiert bereits in der Maske "{window.name}"')
                    }
                )
