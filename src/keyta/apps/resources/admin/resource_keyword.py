from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseDocumentationAdmin

from apps.resources.models import ResourceKeyword, ResourceKeywordDocumentation


@admin.register(ResourceKeyword)
class ResourceKeywordAdmin(BaseDocumentationAdmin):
    list_display = ['resource', 'name', 'short_doc']
    list_filter = ['resource']
    search_fields = ['name']
    search_help_text = _('Name')
    ordering = ['resource__name', 'name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('resource')

    def has_add_permission(self, request):
        return False

@admin.register(ResourceKeywordDocumentation)
class ResourceKeywordDocumentationAdmin(BaseDocumentationAdmin):
    pass
