from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from keyta.models.base_model import AbstractBaseModel

from .variable_value import VariableValue


class VariableType(models.TextChoices):
    DICT = 'DICT', _('Formular')
    LIST = 'LIST', _('Werteliste')


class Variable(AbstractBaseModel):
    name = models.CharField(max_length=255, verbose_name=_('Name'))

    # Customization #
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Beschreibung')
    )
    systems = models.ManyToManyField(
        'systems.System',
        related_name='variables',
        verbose_name=_('Systeme')
    )
    template = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Vorlage')
    )
    type = models.CharField(
        max_length=255,
        choices=sorted(VariableType.choices, key=lambda kv: kv[1]),
        default=VariableType.DICT,
        verbose_name=_('Art')
    )
    windows = models.ManyToManyField(
        'windows.Window',
        related_name='variables',
        verbose_name=_('Masken')
    )

    def __str__(self):
        return self.name

    def add_value(
            self,
            name: str
    ):
        VariableValue.objects.get_or_create(
            name=name,
            variable=self
        )

    def is_dict(self):
        return self.type == VariableType.DICT

    def is_list(self):
        return self.type == VariableType.LIST

    def to_robot(self, get_variable_value):
        if self.is_dict():
            return (
                '&{%s}' % self.name,
                {
                    value.name: get_variable_value(value.pk)
                    for value in self.values.all()
                }
            )

        if self.is_list():
            return ('@{%s}' % self.name, {})

    class Meta:
        ordering = [Lower('name')]
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')


class VariableDocumentation(Variable):
    class Meta:
        proxy = True
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')


class VariableQuickAdd(Variable):
    class Meta:
        proxy = True
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')


class VariableQuickChange(Variable):
    class Meta:
        proxy = True
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')
