from importlib import import_module

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from keyta.rf_import.import_keywords import get_libdoc_dict

from .models import Library


class LibraryForm(forms.ModelForm):
    def clean_name(self):
        name = self.cleaned_data["name"]

        if not name in Library.ROBOT_LIBRARIES:
            try:
                import_module(name)

                if not get_libdoc_dict(name)['keywords']:
                    raise ValidationError(_(f'"{name}" ist keine Robot Framework Bibliothek'))
            except ModuleNotFoundError:
                raise ValidationError(_(f'Die Bibliothek "{name}" ist im PYTHONPATH nicht vorhanden.'))

        return name
