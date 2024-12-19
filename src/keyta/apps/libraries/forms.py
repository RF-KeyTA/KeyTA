from importlib import import_module

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from apps.libraries.models import Library


class LibraryForm(forms.ModelForm):
    def clean_name(self):
        name = self.cleaned_data["name"]

        if not name in Library.ROBOT_LIBRARIES:
            try:
                import_module(name)
            except ModuleNotFoundError as err:
                raise ValidationError(_('Die Bibliothek "{name}" ist nicht vorhanden').format(name=name))

        return name
