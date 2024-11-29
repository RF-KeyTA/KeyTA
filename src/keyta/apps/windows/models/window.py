import re

from django.db import models

from apps.common.abc import AbstractBaseModel


class Window(AbstractBaseModel):
    systems = models.ManyToManyField(
        'systems.System',
        related_name='windows',
        verbose_name='Systeme',
    )
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Beschreibung'
    )
    documentation = models.TextField(verbose_name='Dokumentation')

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
        verbose_name = 'Maske'
        verbose_name_plural = 'Masken'

        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['system', 'name'],
        #         name='unique_window_per_system'
        #     )
        # ]


class WindowDocumentation(Window):
    class Meta:
        proxy = True
        verbose_name = 'Dokumentation der Maske'
        verbose_name_plural = 'Dokumentation der Masken'
