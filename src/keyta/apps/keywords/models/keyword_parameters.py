import re

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _

from model_clone import CloneMixin

from keyta.models.base_model import AbstractBaseModel

from .keyword import Keyword
from .keywordcall_parameter_source import KeywordCallParameterSource


class KeywordParameterType(models.TextChoices):
    ARG = 'ARG', _('Positional Argument')
    KWARG = 'KWARG', _('Optional Argument')


class KeywordParameter(CloneMixin, AbstractBaseModel):
    keyword = models.ForeignKey(
        'keywords.Keyword',
        on_delete=models.CASCADE,
        related_name='parameters'
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('Name')
    )
    position = models.PositiveIntegerField(
        null=True,
        default=0
    )
    default_value = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Standardwert')
    )
    is_list = models.BooleanField(
        default=False
    )
    type = models.CharField(
        max_length=255,
        choices=KeywordParameterType.choices
    )

    USE_UNIQUE_DUPLICATE_SUFFIX = False

    class Manager(models.Manager):
        def args(self):
            return self.get_queryset().filter(type=KeywordParameterType.ARG)

        def kwargs(self):
            return self.get_queryset().filter(type=KeywordParameterType.KWARG)

    objects = Manager()

    def __str__(self):
        return self.name

    @classmethod
    def create_arg(cls, keyword: Keyword, name: str, position: int, is_list=False):
        KeywordParameter.objects.update_or_create(
            keyword=keyword,
            position=position,
            defaults={
                'default_value': '@{EMPTY}' if is_list else None,
                'name': name,
                'type': KeywordParameterType.ARG,
                'is_list': is_list
            }
        )

    @classmethod
    def create_kwarg(cls, keyword: Keyword, name: str, default_value: str):
        KeywordParameter.objects.update_or_create(
            keyword=keyword,
            name=name,
            defaults={
                'default_value': default_value,
                'position': None,
                'type': KeywordParameterType.KWARG
            }
        )

    def save(
        self, force_insert=False, force_update=False, using=None,
        update_fields=None
    ):
        self.name = re.sub(r"\s{2,}", " ", self.name)

        if not self.type:
            self.type = KeywordParameterType.ARG

        if not self.pk:
            super().save(force_insert, force_update, using, update_fields)

            KeywordCallParameterSource.objects.create(kw_param=self)

            for kw_call in (
                self.keyword.uses.keyword_calls() |
                self.keyword.uses.test_steps()
            ):
                kw_call.add_parameter(self)
        else:
            super().save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = ['position']
        constraints = [
            models.UniqueConstraint(
                fields=['keyword', 'name'],
                name='unique_keyword_parameter'
            ),
            models.CheckConstraint(
                name='keyword_parameter_sum_type',
                check=
                (Q(type=KeywordParameterType.ARG) &
                 Q(position__isnull=False))
                |
                (Q(type=KeywordParameterType.KWARG) &
                 Q(position__isnull=True) &
                 Q(default_value__isnull=False))
            )
        ]
        verbose_name = _('Parameter')
        verbose_name_plural = _('Parameters')
