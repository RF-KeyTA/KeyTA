from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WindowsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.windows'
    verbose_name = _('Masken')
