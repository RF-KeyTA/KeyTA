from django.utils.translation import gettext as _

from apps.executions.admin import SetupTeardownInline
from apps.executions.models import KeywordExecutionSetup


class KeywordExecutionSetupInline(SetupTeardownInline):
    model = KeywordExecutionSetup
    fields = ['enabled', 'user', 'to_keyword', 'args']
    extra = 0
    max_num = 1
    verbose_name_plural = _('Anbindung an ein laufendes System')
