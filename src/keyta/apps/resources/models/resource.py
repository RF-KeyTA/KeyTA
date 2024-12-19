from django.db import models
from django.utils.translation import gettext as _


class Resource(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))
    documentation = models.TextField(verbose_name=_('Dokumentation'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Ressource')
        verbose_name_plural = _('Ressourcen')
