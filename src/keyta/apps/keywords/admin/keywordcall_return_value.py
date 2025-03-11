from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models import KeywordCallReturnValue


# This admin is necessary in order to delete a KeywordCallReturnValue
@admin.register(KeywordCallReturnValue)
class KeywordCallReturnValueAdmin(BaseAdmin):
    pass
