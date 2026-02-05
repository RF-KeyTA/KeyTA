from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SequencesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'keyta.apps.sequences'
    verbose_name = _('Sequenzen')
