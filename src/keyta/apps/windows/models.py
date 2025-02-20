from django.utils.translation import gettext as _

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


class SystemWindow(Window):
    class Meta:
        proxy = True
        verbose_name = _('Maske')
        verbose_name_plural = _('Masken')
