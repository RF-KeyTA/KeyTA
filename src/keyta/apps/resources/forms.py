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

        if err := Resource.resource_file_not_found(filename):
            raise ValidationError(err)

        return file
