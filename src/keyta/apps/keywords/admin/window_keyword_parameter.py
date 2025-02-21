from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models import WindowKeywordParameter


# This admin is necessary for the delete field
#  in the Parameters inline to work
@admin.register(WindowKeywordParameter)
class WindowKeywordParameterAdmin(BaseAdmin):
    pass
