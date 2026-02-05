from django.utils.translation import gettext_lazy as _

from keyta.models.base_model import AbstractBaseModel

from .variable import Variable


class VariableWindowRelation(AbstractBaseModel, Variable.windows.through):
    def __str__(self):
        return str(self.window)

    class Meta:
        proxy = True
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')
