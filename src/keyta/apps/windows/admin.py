from django.contrib import admin

from keyta.admin.base_admin import BaseDocumentationAdmin
from keyta.admin.window import BaseWindowAdmin

from .models import Window, WindowDocumentation, WindowQuickAdd


@admin.register(Window)
class WindowAdmin(BaseWindowAdmin):
    pass


@admin.register(WindowDocumentation)
class WindowDocumentationAdmin(BaseDocumentationAdmin):
    pass


@admin.register(WindowQuickAdd)
class SystemWindowAdmin(BaseWindowAdmin):
    pass
