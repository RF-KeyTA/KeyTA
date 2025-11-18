from abc import ABCMeta

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse


class AbstractModelMeta(ABCMeta, type(models.Model)):
    pass


class AbstractBaseModel(models.Model, metaclass=AbstractModelMeta):
    def get_admin_url(self, app=None, absolute=False):
        app_model = (app or self._meta.app_label, self._meta.model_name)
        url = reverse('admin:%s_%s_change' % app_model, args=(self.pk,))

        if absolute:
            return settings.BASE_URL + url

        return url

    def get_delete_url(self):
        app_model = (self._meta.app_label, self._meta.model_name)
        return reverse('admin:%s_%s_delete' % app_model, args=(self.pk,))

    def get_tab_url(self, tab_name=None):
        return '#' + slugify(tab_name or self._meta.verbose_name_plural) + '-tab'

    class Meta:
        abstract = True
