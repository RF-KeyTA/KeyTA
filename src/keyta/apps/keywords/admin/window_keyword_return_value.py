from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models import WindowKeywordReturnValue


# This admin is necessary for the delete field
# in the Return Values inline to work
@admin.register(WindowKeywordReturnValue)
class WindowKeywordReturnValueAdmin(BaseAdmin):
    pass
