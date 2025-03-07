from importlib import import_module

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import Library


class LibraryForm(forms.ModelForm):
    def clean_name(self):
        name = self.cleaned_data["name"]

        if not name in Library.ROBOT_LIBRARIES:
            try:
                import_module(name)
            except ModuleNotFoundError as err:
                raise ValidationError(_(f'Die Bibliothek "{name}" ist im PYTHONPATH nicht vorhanden.'))

        return name
