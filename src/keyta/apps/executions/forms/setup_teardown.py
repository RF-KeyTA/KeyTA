from django import forms

from keyta.apps.keywords.models import KeywordCall


class SetupTeardownForm(forms.ModelForm):
    def save(self, commit=True):
        kw_call: KeywordCall = super().save(commit)

        if kw_call.pk and 'to_keyword' in self.changed_data:
            for param in kw_call.parameters.all():
                param.delete()

        return kw_call
