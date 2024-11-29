from django.contrib.auth.models import User

from apps.executions.models import KeywordExecution
from apps.keywords.models import KeywordCall
from apps.libraries.models import LibraryImport

from .sequence import Sequence


class SequenceExecution(KeywordExecution):
    def get_testsuite(self, user: User):
        sequence = Sequence.objects.get(pk=self.keyword.pk)
        keywords = {sequence.pk: sequence.to_robot()}

        for action in sequence.actions:
            keywords[action.pk] = action.to_robot()

        return super().to_robot(
            keywords,
            user
        )

    def update_library_imports(self, library_ids: set[int], user: User):
        action_ids = KeywordCall.objects.filter(from_keyword_id=self.keyword.pk).values_list('to_keyword_id', flat=True)

        for lib_id in LibraryImport.objects.filter(keyword_id__in=action_ids).values_list('library_id').distinct():
            library_ids.update(lib_id)

        super().update_library_imports(library_ids, user)

    def update_resource_imports(self, resource_ids: set[int], user: User):
        sequence = Sequence.objects.get(pk=self.keyword.pk)

        super().update_resource_imports(sequence.resource_ids, user)


    class Meta:
        proxy = True
        verbose_name = 'Ausführung'
        verbose_name_plural = 'Ausführung'
