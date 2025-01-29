from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _


class LibraryImportParameter(models.Model):
    library_import = models.ForeignKey(
        'libraries.LibraryImport',
        on_delete=models.CASCADE,
        related_name='kwargs'
    )
    library_parameter = models.ForeignKey(
        'libraries.LibraryParameter',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )
    value = models.CharField(max_length=255, verbose_name=_('Wert'))

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.library_parameter.name

    class Meta:
        verbose_name = _('Parameter')
        verbose_name_plural = _('Parameters')
