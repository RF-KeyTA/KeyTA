from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _

from model_clone import CloneMixin

from . import KeywordCall
from .execution_keywordcall import ExecutionKeywordCall
from .keyword import Keyword
from .keyword_return_value import KeywordReturnValue


class WindowKeyword(CloneMixin, Keyword):
    _clone_linked_m2m_fields = ['systems', 'windows']
    _clone_m2o_or_o2m_fields = ['calls', 'parameters', 'return_value']
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
        attrs = attrs or {'name': self.name + _(' Kopie')}
        clone: WindowKeyword = super().make_clone(attrs=attrs, sub_clone=sub_clone, using=using, parent=parent)

        return_value: KeywordReturnValue
        if return_value := clone.return_value.first():
            return_value.kw_call_return_value = clone.calls.get(index=return_value.kw_call_index).return_values.first()
            return_value.save()

        execution_kw_call: KeywordCall = clone.execution.keyword_calls.first()

        # Delete the parameters of the execution keyword call
        # so that they get updated in the ExecutionKeywordCallAdmin
        for param in execution_kw_call.parameters.all():
            param.delete()

        return clone

    class Meta(Keyword.Meta):
        proxy = True
