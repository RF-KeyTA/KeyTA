from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from keyta.apps.actions.models import Action
from keyta.apps.keywords.models import WindowKeyword
from keyta.apps.keywords.models.keyword import KeywordType


class Sequence(WindowKeyword):
    @property
    def actions(self):
        return Action.objects.filter(
            id__in=self.calls.values_list('to_keyword__pk', flat=True)
        )

    def lock(self):
        self.locked = True
        self.save()

    @property
    def resource_ids(self) -> set[int]:
        return set(self.resource_imports.values_list('resource_id', flat=True))

    def save(
        self, force_insert=False, force_update=False,
        using=None, update_fields=None
    ):
        self.type = KeywordType.SEQUENCE
        return super().save(force_insert, force_update, using, update_fields)

    def unlock(self):
        self.locked = False
        self.last_unlocked = timezone.now()
        self.save()

    @property
    def unlock_timeout_expired(self):
        dt = timezone.localtime() - self.last_unlocked
        return dt.seconds / 60 > 1

    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .filter(type=KeywordType.SEQUENCE)
            )

    objects = Manager()

    class Meta(WindowKeyword.Meta):
        proxy = True
        verbose_name = _('Sequenz')
        verbose_name_plural = _('Sequenzen')


class SequenceQuickAdd(Sequence):
    class Meta:
        proxy = True
        verbose_name = _('Sequenz')
        verbose_name_plural = _('Sequenzen')


class SequenceQuickChange(Sequence):
    class Meta:
        proxy = True
        verbose_name = _('Sequenz')
        verbose_name_plural = _('Sequenzen')
