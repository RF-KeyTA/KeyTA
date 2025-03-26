from django.db import models
from django.utils.translation import gettext as _

from keyta.apps.keywords.models import WindowKeyword
from keyta.apps.keywords.models.keyword import KeywordType
from keyta.apps.keywords.models.keywordcall import KeywordCallType
from keyta.apps.libraries.models import LibraryImport
from keyta.models.base_model import AbstractBaseModel


class Action(WindowKeyword):
    _clone_m2o_or_o2m_fields = WindowKeyword._clone_m2o_or_o2m_fields + ['library_imports']

    def has_dependents(self):
        return self.uses.exclude(type=KeywordCallType.KEYWORD_EXECUTION).exists()

    def depends_on_library(self, library_pk: int):
        return self.calls.filter(to_keyword__library__id=library_pk).exists()

    def depends_on(self, obj):
        if isinstance(obj, LibraryImport):
            return self.depends_on_library(obj.library.pk)

        if isinstance(obj, ActionWindowRelation):
            return self.has_dependents()

        return False

    @property
    def library_ids(self) -> set[int]:
        return set(self.library_imports.values_list('library_id', flat=True))

    def save(
            self, force_insert=False, force_update=False,
            using=None, update_fields=None
    ):
        if not self.pk:
            self.type = KeywordType.ACTION

        super().save(force_insert, force_update, using, update_fields)

    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .filter(type=KeywordType.ACTION)
            )

    objects = Manager()

    class Meta(WindowKeyword.Meta):
        proxy = True
        verbose_name = _('Aktion')
        verbose_name_plural = _('Aktionen')


class ActionQuickAdd(Action):
    class Meta:
        proxy = True
        verbose_name = _('Aktion')
        verbose_name_plural = _('Aktionen')


class ActionQuickChange(Action):
    class Meta:
        proxy = True
        verbose_name = _('Aktion')
        verbose_name_plural = _('Aktionen')


class ActionWindowRelation(AbstractBaseModel, Action.windows.through):
    def __str__(self):
        return f'{self.keyword} -> {self.window}'

    class Meta:
        auto_created = True
        proxy = True
        verbose_name = _('Beziehung zu Maske')
        verbose_name_plural = _('Beziehungen zu Masken')
