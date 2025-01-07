from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from apps.executions.models import KeywordExecution

from .action import Action


class ActionExecution(KeywordExecution):
    def get_testsuite(self, user: User) -> dict:
        action = Action.objects.get(id=self.keyword.pk)

        return super().to_robot(
            {action.id: action.to_robot()},
            user
        )

    def update_resource_imports(self, resource_ids: set[int], user: User):
        action = Action.objects.get(pk=self.keyword.pk)

        super().update_library_imports(action.library_ids, user)

    class Meta:
        proxy = True
        verbose_name = _('Ausführung')
        verbose_name_plural = _('Ausführung')
