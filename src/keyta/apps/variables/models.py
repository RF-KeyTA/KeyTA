from django.utils.translation import gettext as _

from keyta.models.base_model import AbstractBaseModel
from keyta.models.variable import AbstractVariable, AbstractVariableValue


class Variable(AbstractVariable):
    pass


class VariableValue(AbstractVariableValue):
    pass


class VariableWindow(AbstractBaseModel, Variable.windows.through):
    def __str__(self):
        return str(self.window)

    class Meta:
        auto_created = True
        proxy = True
        verbose_name = _('Beziehung zu Maske')
        verbose_name_plural = _('Beziehungen zu Masken')


class WindowVariable(Variable):
    def __str__(self):
        return str(self.name)

    class Meta:
        proxy = True
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')
