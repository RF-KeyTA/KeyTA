from django.contrib import admin

from admin.base_admin import BaseAdmin

from ..models import KeywordParameter


@admin.register(KeywordParameter)
class KeywordParameterAdmin(BaseAdmin):
    pass
