from apps.common.forms import BaseForm
from apps.keywords.models import Keyword, KeywordCall


class StepsForm(BaseForm):
    def save(self, commit=True):
        kw_call: KeywordCall = super().save(commit)

        if kw_call.pk and 'to_keyword' in self.changed_data:
            to_keyword: Keyword = self.cleaned_data['to_keyword']

            for param in kw_call.parameters.all():
                param.delete()

            for param in to_keyword.parameters.all():
                kw_call.add_parameter(param)

        return kw_call
