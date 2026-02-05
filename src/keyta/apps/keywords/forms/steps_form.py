from keyta.forms import BaseForm

from ..models import KeywordCall


class StepsForm(BaseForm):
    def save(self, commit=True):
        kw_call: KeywordCall = super().save(commit)

        if kw_call.pk:
            if 'window' in self.changed_data:
                kw_call.to_keyword = None
                kw_call.delete_parameters()
                kw_call.save()

            if all([
                self.initial.get('to_keyword', None),
                'to_keyword' in self.changed_data
            ]):
                kw_call.delete_conditions()
                kw_call.delete_parameters()
                kw_call.delete_return_values()

        return kw_call
