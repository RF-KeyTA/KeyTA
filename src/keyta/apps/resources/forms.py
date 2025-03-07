import os
import sys

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import Resource


class ResourceForm(forms.ModelForm):
    def clean_name(self):
        file = self.cleaned_data["name"]
        filename = str(file)

        if Resource.objects.filter(name=filename.rstrip('.resource')).exists():
            raise ValidationError(_(f'Die Ressource "{filename}" ist bereits vorhanden.'))

        for dire in [item for item in sys.path if os.path.isdir(item)]:
            candidate = os.path.normpath(os.path.join(dire, filename))
            if os.path.isfile(candidate):
                return file

        raise ValidationError(_(f'Die Ressource "{filename}" ist im PYTHONPATH nicht vorhanden.'))
