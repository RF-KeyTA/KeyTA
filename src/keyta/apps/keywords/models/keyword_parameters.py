import json
import re

from django.db import models
from django.utils.translation import gettext_lazy as _

from model_clone import CloneMixin

from keyta.models.base_model import AbstractBaseModel

from .keywordcall_parameter_source import KeywordCallParameterSource


class KeywordParameterType(models.TextChoices):
    ARG = 'ARG', _('Positional Argument')
    KWARG = 'KWARG', _('Optional Argument')
    VAR_ARG = 'VAR_ARG', _('Variadic Argument')
    VAR_KWARG = 'VAR_KWARG', _('Variadic Named Argument')


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
        default=0
    )
    default_value = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Standardwert')
    )
    type = models.CharField(
        max_length=255,
        choices=KeywordParameterType.choices
    )
    # JSON representation of a union type as a list of strings
    typedoc = models.CharField(
        max_length=255,
        default='[]'
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
    def create_arg(cls, keyword, name: str, position: int, typedoc: list[str]):
        kw_param, created = KeywordParameter.objects.update_or_create(
            keyword=keyword,
            position=position,
            defaults={
                'default_value': None,
                'name': name,
                'type': KeywordParameterType.ARG
            }
        )
        kw_param.set_typedoc(typedoc)

    @classmethod
    def create_kwarg(cls, keyword, name: str, default_value: str, position: int, typedoc: list[str]):
        kw_param, created = KeywordParameter.objects.update_or_create(
            keyword=keyword,
            name=name,
            defaults={
                'default_value': default_value,
                'position': position,
                'type': KeywordParameterType.KWARG
            }
        )
        kw_param.set_typedoc(typedoc)

    @classmethod
    def create_vararg(cls, keyword, name: str, position: int, typedoc: list[str]):
        kw_param, created = KeywordParameter.objects.update_or_create(
            keyword=keyword,
            position=position,
            defaults={
                'default_value': '@{EMPTY}',
                'name': name,
                'type': KeywordParameterType.VAR_ARG,
            }
        )
        kw_param.set_typedoc(typedoc)

    @classmethod
    def create_varkwarg(cls, keyword, name: str, position: int, typedoc: list[str]):
        kw_param, created = KeywordParameter.objects.update_or_create(
            keyword=keyword,
            position=position,
            defaults={
                'default_value': '&{EMPTY}',
                'name': name,
                'type': KeywordParameterType.VAR_KWARG,
            }
        )
        kw_param.set_typedoc(typedoc)

    def get_typedoc(self) -> list[str]:
        return json.loads(self.typedoc)

    @property
    def is_arg(self):
        return self.type == KeywordParameterType.ARG

    @property
    def is_kwarg(self):
        return self.type == KeywordParameterType.KWARG

    @property
    def is_vararg(self):
        return self.type == KeywordParameterType.VAR_ARG

    @property
    def is_varkwarg(self):
        return self.type == KeywordParameterType.VAR_KWARG

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

            for kw_call in self.keyword.uses.keyword_calls():
                kw_call.add_parameter(self)
        else:
            super().save(force_insert, force_update, using, update_fields)

    def set_typedoc(self, typedoc: list[str]):
        self.typedoc = json.dumps(typedoc)
        self.save()

    class Meta:
        ordering = ['position']
        constraints = [
            models.UniqueConstraint(
                fields=['keyword', 'name'],
                name='unique_keyword_parameter'
            )
        ]
        verbose_name = _('Parameter')
        verbose_name_plural = _('Parameters')
