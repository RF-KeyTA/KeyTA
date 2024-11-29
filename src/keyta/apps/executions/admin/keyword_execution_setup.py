from django.contrib import admin

from .setup_teardown import SetupTeardownAdmin
from ..models import KeywordExecutionSetup


@admin.register(KeywordExecutionSetup)
class KeywordExecutionSetupAdmin(SetupTeardownAdmin):
    pass
