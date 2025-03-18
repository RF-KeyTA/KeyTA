from keyta.forms import BaseForm

from ..models import KeywordCall


class StepsForm(BaseForm):
    def save(self, commit=True):
        kw_call: KeywordCall = super().save(commit)

        if kw_call.pk:
            if 'window' in self.changed_data:
                kw_call.to_keyword = None
                kw_call.variable = None
                kw_call.save()

            if 'to_keyword' in self.changed_data:
                for param in kw_call.parameters.all():
                    param.delete()

                for return_value in kw_call.return_values.all():
                    return_value.delete()

        return kw_call
