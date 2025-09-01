from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from model_clone import CloneMixin

from . import KeywordCall
from .execution_keywordcall import ExecutionKeywordCall
from .keyword import Keyword
from .keyword_return_value import KeywordReturnValue


class WindowKeyword(CloneMixin, Keyword):
    _clone_linked_m2m_fields = ['systems', 'windows']
    _clone_m2o_or_o2m_fields = ['calls', 'parameters', 'return_values']
    _clone_o2o_fields = ['execution']

    def create_execution(self, user: AbstractUser):
        Execution = apps.get_model('executions', 'Execution')
        execution = Execution.objects.create(keyword=self)
        kw_call = ExecutionKeywordCall.objects.create(
            execution=execution,
            to_keyword=self,
        )

        for param in self.parameters.all():
            kw_call.add_parameter(param, user)

        library_ids = self.systems.values_list('library', flat=True).distinct()

        Library = apps.get_model('libraries', 'Library')
        LibraryImport = apps.get_model('libraries', 'LibraryImport')

        for library in Library.objects.filter(id__in=library_ids):
            LibraryImport.objects.create(
                execution=execution,
                library=library
            )

    def make_clone(self, attrs=None, sub_clone=False, using=None, parent=None) -> Keyword:
        copies = self._meta.model.objects.filter(name__istartswith=self.name + _(' Kopie')).count()
        attrs = (attrs or {}) | {'name': self.name + _(' Kopie ') + str(copies)}

        clone: WindowKeyword = super().make_clone(attrs=attrs, sub_clone=sub_clone, using=using, parent=parent)
        clone_return_values: list[KeywordReturnValue] = list(clone.return_values.all())
        kw_call_indices = [return_value.kw_call_index for return_value in clone_return_values]
        clone_kw_call_return_values = {
            index: {
                str(kw_call_return_value): kw_call_return_value
                for kw_call_return_value in clone.calls.get(index=index).return_values.all()
            }
            for index in kw_call_indices
        }

        clone_return_value: KeywordReturnValue
        for clone_return_value in clone_return_values:
            clone_return_value.kw_call_return_value = clone_kw_call_return_values[clone_return_value.kw_call_index][str(clone_return_value.kw_call_return_value)]
            clone_return_value.save()

        execution_kw_call: KeywordCall = clone.execution.keyword_calls.first()
        execution_kw_call.to_keyword = clone
        execution_kw_call.save()

        # Delete the parameters of the execution keyword call
        # so that they get updated in the ExecutionKeywordCallAdmin
        for param in execution_kw_call.parameters.all():
            param.delete()

        return clone

    class Meta(Keyword.Meta):
        proxy = True
