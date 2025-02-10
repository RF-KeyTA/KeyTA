from django.contrib import admin
from django.utils.translation import gettext as _

from ..models import ResourceImport


class ResourceImportsInline(admin.TabularInline):
    model = ResourceImport
    fields = ['resource']
    readonly_fields = ['resource']
    extra = 0
    max_num = 0
    can_delete = False
    verbose_name_plural = _('Ressourcen')
