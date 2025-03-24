import re

from django.db import models
from django.utils.translation import gettext as _

from keyta.apps.keywords.models import KeywordCall
from keyta.apps.resources.models import ResourceImport
from keyta.models.base_model import AbstractBaseModel


class AbstractWindow(AbstractBaseModel):
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

    def depends_on_resource(self, resource_pk: int):
        return (
            KeywordCall.objects.filter(from_keyword__id__in=self.sequences) |
            KeywordCall.objects.filter(window=self)
        ).filter(to_keyword__resource__id=resource_pk).exists()

    def depends_on(self, obj):
        if isinstance(obj, ResourceImport):
            return self.depends_on_resource(obj.resource.pk)

        return False

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
        abstract = True
        ordering = ['name']
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['system', 'name'],
        #         name='unique_window_per_system'
        #     )
        # ]
