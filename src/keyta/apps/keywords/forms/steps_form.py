from keyta.forms import BaseForm

from ..models import KeywordCall, KeywordCallParameter, KeywordReturnValue


class StepsForm(BaseForm):
    def save(self, commit=True):
        kw_call: KeywordCall = super().save(commit)

        if kw_call.pk:
            if 'window' in self.changed_data:
                kw_call.to_keyword = None
                kw_call.variable = None
                kw_call.save()

            if self.initial.get('to_keyword', None) and 'to_keyword' in self.changed_data:
                param: KeywordCallParameter
                for param in kw_call.parameters.all():
                    param.delete()

                kw_call.variable = None
                kw_call.save()

                return_value: KeywordReturnValue
                for return_value in kw_call.return_values.all():
                    return_value.delete()

                if return_value := kw_call.to_keyword.return_value.first():
                    kw_call.add_return_value(return_value)

            if self.initial.get('variable', None) and 'variable' in self.changed_data:
                param: KeywordCallParameter
                for param in kw_call.parameters.all():
                    if param.value_ref:
                        param.reset_value()
                        param.save()

        return kw_call
