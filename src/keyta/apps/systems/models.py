from django.db import models
from django.utils.translation import gettext as _

from apps.common.abc import AbstractBaseModel
from apps.keywords.models import Keyword
from apps.libraries.models import Library, LibraryKeyword


class System(AbstractBaseModel):
    attach_to_system = models.ForeignKey(
        Keyword,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Anbindung an laufendes System')
    )
    library = models.ForeignKey(
        Library,
        on_delete=models.PROTECT,
        verbose_name=_('Automatisierung')
    )
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))
    description = models.CharField(max_length=255, verbose_name=_('Beschreibung'))
    client = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Mandant')
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('System')
        verbose_name_plural = _('Systeme')
