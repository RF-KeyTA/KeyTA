from pathlib import Path

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Resource


class ResourceForm(forms.ModelForm):
    def clean_path(self):
        filepath = Path(self.cleaned_data["path"]).as_posix()

        if not filepath.endswith('.resource'):
            raise ValidationError(_('Der Dateipfad muss mit .resource enden'))

        if not self.instance.pk and Resource.objects.filter(path=filepath).exists():
            raise ValidationError(_(f'Die Ressource "{filepath}" ist bereits vorhanden.'))

        if err := Resource.resource_file_not_found(filepath):
            raise ValidationError(err)

        return filepath
