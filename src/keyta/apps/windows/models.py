from django.utils.translation import gettext as _

from keyta.models.base_model import AbstractBaseModel
from keyta.models.window import AbstractWindow


class Window(AbstractWindow):
    class Meta(AbstractWindow.Meta):
        verbose_name = _('Maske')
        verbose_name_plural = _('Masken')


class WindowDocumentation(Window):
    class Meta:
        proxy = True
        verbose_name = _('Dokumentation der Maske')
        verbose_name_plural = _('Dokumentation der Masken')


class WindowQuickAdd(Window):
    class Meta:
        proxy = True
        verbose_name = _('Maske')
        verbose_name_plural = _('Masken')


class WindowSystemRelation(AbstractBaseModel, Window.systems.through):
    def __str__(self):
        return str(self.window)

    class Meta:
        auto_created = True
        proxy = True
        verbose_name = _('Beziehung zum System')
        verbose_name_plural = _('Beziehungen zu Systemen')
