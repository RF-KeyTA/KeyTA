from django.utils.translation import gettext_lazy as _

from keyta.models.base_model import AbstractBaseModel

from .action import Action


class ActionWindowRelation(AbstractBaseModel, Action.windows.through):
    def __str__(self):
        return f'{self.window}'

    class Meta:
        auto_created = True
        proxy = True
        verbose_name = _('Zuweisung zur Maske')
        verbose_name_plural = _('Zuweisungen zu Masken')
