from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LibrariesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'keyta.apps.libraries'
    verbose_name = _('Bibliotheken')
