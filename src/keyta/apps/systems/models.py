from django.utils.translation import gettext as _

from keyta.models.system import AbstractSystem


class System(AbstractSystem):
    class Meta:
        verbose_name = _('System')
        verbose_name_plural = _('Systeme')
