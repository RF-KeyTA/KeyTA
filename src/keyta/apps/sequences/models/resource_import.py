from django.db import models
from django.utils.translation import gettext as _

from apps.resources.models import ResourceImport


class SequenceResourceImport(ResourceImport):
    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super().
                get_queryset()
                .only('resource')
                .order_by('resource__name')
            )

    objects = Manager()

    class Meta:
        proxy = True
        verbose_name = _('Ressource-Import')
        verbose_name_plural = _('Ressource-Imports')
