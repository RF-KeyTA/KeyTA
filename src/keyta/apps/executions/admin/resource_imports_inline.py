from django.contrib import admin

from apps.executions.models import ExecutionResourceImport


class ResourceImportsInline(admin.TabularInline):
    model = ExecutionResourceImport
    fields = ['resource']
    readonly_fields = ['resource']
    extra = 0
    max_num = 0
    can_delete = False
    verbose_name_plural = 'Ressourcen'
