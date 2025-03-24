from abc import ABCMeta

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse


class AbstractModelMeta(ABCMeta, type(models.Model)):
    pass


class AbstractBaseModel(models.Model, metaclass=AbstractModelMeta):
    def depends_on(self, obj):
        return False

    def get_admin_url(self, model=None):
        app_model = (self._meta.app_label, model or self._meta.model_name)
        return reverse('admin:%s_%s_change' % app_model, args=(self.pk,))

    def get_delete_url(self):
        app_model = (self._meta.app_label, self._meta.model_name)
        return reverse('admin:%s_%s_delete' % app_model, args=(self.pk,))

    def get_tab_url(self, tab_name=None):
        return '#' + slugify(tab_name or self._meta.verbose_name_plural) + '-tab'

    class Meta:
        abstract = True
