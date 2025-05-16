from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class VariablesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'keyta.apps.variables'
    verbose_name = _('Referenzwerte')