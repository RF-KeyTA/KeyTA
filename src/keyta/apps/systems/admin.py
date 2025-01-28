from django.contrib import admin

from keyta.admin.system import BaseSystemAdmin

from .models import System


@admin.register(System)
class SystemAdmin(BaseSystemAdmin):
   pass
