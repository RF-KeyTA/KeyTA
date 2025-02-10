from django.db import models
from django.utils.translation import gettext as _

from apps.actions.models import Action
from keyta.apps.keywords.models import WindowKeyword
from keyta.apps.keywords.models.keyword import KeywordType


class Sequence(WindowKeyword):
    @property
    def actions(self):
        return Action.objects.filter(
            id__in=self.calls.values_list('to_keyword__pk', flat=True)
        )

    def save(
        self, force_insert=False, force_update=False,
        using=None, update_fields=None
    ):
        self.type = KeywordType.SEQUENCE
        return super().save(force_insert, force_update, using, update_fields)

    @property
    def resource_ids(self) -> set[int]:
        return set(self.resource_imports.values_list('resource_id', flat=True))


    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .filter(type=KeywordType.SEQUENCE)
            )

    objects = Manager()

    class Meta:
        proxy = True
        verbose_name = _('Sequenz')
        verbose_name_plural = _('Sequenzen')


class SequenceDocumentation(Sequence):
    class Meta:
        proxy = True
        verbose_name = _('Sequenz Dokumentation')


class WindowSequence(Sequence):
    def __str__(self):
        return str(self.name)

    class Meta:
        proxy = True
        verbose_name = _('Sequenz')
        verbose_name_plural = _('Sequenzen')
