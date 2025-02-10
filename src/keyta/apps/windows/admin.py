from django.contrib import admin

from keyta.admin.base_admin import BaseDocumentationAdmin
from keyta.admin.window import BaseWindowAdmin

from apps.windows.models import Window, WindowDocumentation, SystemWindow


@admin.register(Window)
class WindowAdmin(BaseWindowAdmin):
    pass


@admin.register(WindowDocumentation)
class WindowDocumentationAdmin(BaseDocumentationAdmin):
    pass


@admin.register(SystemWindow)
class SystemWindowAdmin(BaseWindowAdmin):
    pass
