from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ActionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'keyta.apps.actions'
    verbose_name = _('Aktionen')
