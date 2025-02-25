from keyta.forms import BaseForm

from ..models import KeywordCall


class StepsForm(BaseForm):
    def save(self, commit=True):
        kw_call: KeywordCall = super().save(commit)

        if kw_call.pk and 'to_keyword' in self.changed_data:
            for param in kw_call.parameters.all():
                param.delete()

            if return_value := kw_call.return_value.first():
                return_value.delete()

        return kw_call
