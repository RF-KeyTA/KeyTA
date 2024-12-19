import re

from django.db import models
from django.utils.translation import gettext as _

from apps.common.abc import AbstractBaseModel


class Window(AbstractBaseModel):
    systems = models.ManyToManyField(
        'systems.System',
        related_name='windows',
        verbose_name=_('Systeme'),
    )
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Beschreibung')
    )
    documentation = models.TextField(verbose_name=_('Dokumentation'))

    def __str__(self):
        return self.name

    @property
    def actions(self):
        return self.keywords.actions()

    @property
    def library_ids(self):
        return set((self.systems.values_list('library', flat=True)))

    def save(
        self, force_insert=False, force_update=False, using=None,
            update_fields=None
    ):
        self.name = re.sub(r"\s{2,}", ' ', self.name)
        super().save(force_insert, force_update, using, update_fields)

    @property
    def sequences(self):
        return self.keywords.sequences()

    class Meta:
        verbose_name = _('Maske')
        verbose_name_plural = _('Masken')

        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['system', 'name'],
        #         name='unique_window_per_system'
        #     )
        # ]


class WindowDocumentation(Window):
    class Meta:
        proxy = True
        verbose_name = _('Dokumentation der Maske')
        verbose_name_plural = _('Dokumentation der Masken')
