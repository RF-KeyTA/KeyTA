import re

from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from keyta.apps.actions.models import Action
from keyta.apps.keywords.models import KeywordCall
from keyta.apps.resources.models import ResourceImport
from keyta.apps.sequences.models import Sequence
from keyta.models.base_model import AbstractBaseModel


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
        return Action.objects.filter(pk__in=self.keywords.actions())

    def depends_on_resource(self, resource_pk: int):
        return (
            KeywordCall.objects.filter(from_keyword__id__in=self.sequences) |
            KeywordCall.objects.filter(window=self)
        ).filter(to_keyword__resource__id=resource_pk).exists()

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
        return Sequence.objects.filter(pk__in=self.keywords.sequences())

    class Meta:
        ordering = [Lower('name')]
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['system', 'name'],
        #         name='unique_window_per_system'
        #     )
        # ]
        verbose_name = _('Maske')
        verbose_name_plural = _('Masken')


class WindowDocumentation(Window):
    class Meta:
        proxy = True
        verbose_name = _('Dokumentation der Maske')
        verbose_name_plural = _('Dokumentation der Masken')


class WindowQuickAdd(Window):
    class Meta:
        proxy = True
        verbose_name = _('Maske')
        verbose_name_plural = _('Masken')


class WindowQuickChange(Window):
    class Meta:
        proxy = True
        verbose_name = _('Maske')
        verbose_name_plural = _('Masken')


class WindowSystemRelation(AbstractBaseModel, Window.systems.through):
    def __str__(self):
        return f'{self.window} -> {self.system}'

    class Meta:
        auto_created = True
        proxy = True
        verbose_name = _('Beziehung zum System')
        verbose_name_plural = _('Beziehungen zu Systemen')
