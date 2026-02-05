from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models import KeywordCallCondition


@admin.register(KeywordCallCondition)
class KeywordCallConditionAdmin(BaseAdmin):
    pass
