from django import forms
from django.utils.translation import gettext as _

from keyta.forms import BaseForm


class SequenceForm(BaseForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        systems = self.cleaned_data.get('systems')
        windows = self.cleaned_data.get('windows')
        sequence_systems = [
            system.name
            for system in self.initial.get('systems', [])
        ]

        if systems:
            if system := systems.values_list('name', flat=True).exclude(name__in=sequence_systems).filter(keywords__name__iexact=name).first():
                if windows:
                    sequence = self._meta.model.objects.filter(name__iexact=name).filter(systems__name=system).filter(windows__in=windows)
                    window = windows.first()

                    if sequence.exists():
                        raise forms.ValidationError(
                            {
                                "name": _(f'Eine Sequenz mit diesem Namen existiert bereits in der Maske "{window.name}"')
                            }
                        )


class QuickAddSequenceForm(BaseForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        windows = self.cleaned_data.get('windows')

        if len(windows) == 1:
            window = windows[0]
            if window.sequences.filter(name__iexact=name).exists():
                raise forms.ValidationError(
                    {
                        "name": _(f'Eine Sequenz mit diesem Namen existiert bereits in der Maske "{window.name}"')
                    }
                )
