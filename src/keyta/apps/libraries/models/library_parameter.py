from django.db import models
from django.utils.translation import gettext_lazy as _

from keyta.models.base_model import AbstractBaseModel


__all__ = ['LibraryParameter']


class LibraryParameter(AbstractBaseModel):
    library = models.ForeignKey(
        'libraries.Library',
        on_delete=models.CASCADE,
        related_name='kwargs'
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('Name')
    )
    default_value = models.CharField(
        max_length=255,
        verbose_name=_('Standardwert')
    )
    orig_default_value = models.CharField(
        max_length=255
    )

    def __str__(self):
        return self.name

    def reset_value(self):
        self.default_value = self.orig_default_value
        self.save()

    def save(
        self, force_insert=False, force_update=False, using=None,
            update_fields=None
    ):
        if not self.pk:
            self.orig_default_value = self.default_value

        super().save(force_insert, force_update, using, update_fields)

    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().order_by('name')

    objects = Manager()

    class Meta:
        verbose_name = _('Einstellung')
        verbose_name_plural = _('Einstellungen')

        constraints = [
            models.UniqueConstraint(
                fields=['library', 'name'],
                name='unique_library_parameter'
            )
        ]
