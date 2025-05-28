from django.db import models
from django.utils.translation import gettext_lazy as _

from keyta.models.base_model import AbstractBaseModel


class System(AbstractBaseModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('Name')
    )
    description = models.CharField(
        max_length=255,
        verbose_name=_('Beschreibung')
    )
    attach_to_system = models.ForeignKey(
        'keywords.Keyword',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Anbindung an laufendes System')
    )
    library = models.ForeignKey(
        'libraries.Library',
        on_delete=models.PROTECT,
        verbose_name=_('Automatisierung')
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _('System')
        verbose_name_plural = _('Systeme')
