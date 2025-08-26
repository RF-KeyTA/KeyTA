from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models import KeywordCallParameter


# This admin is necessary in order to delete args in the varargs inline
@admin.register(KeywordCallParameter)
class KeywordCallParameterAdmin(BaseAdmin):
    pass
