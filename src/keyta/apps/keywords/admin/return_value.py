from django.contrib import admin

from admin.base_admin import BaseAdmin

from ..models import KeywordReturnValue


@admin.register(KeywordReturnValue)
class ReturnValueAdmin(BaseAdmin):
    pass
