from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseDocumentationAdmin

from ..models import LibraryKeywordDocumentation, LibraryKeyword


@admin.register(LibraryKeyword)
class LibraryKeywordAdmin(BaseDocumentationAdmin):
    list_display = ['library', 'name', 'short_doc']
    list_filter = ['library']
    list_display_links = ['name']
    search_fields = ['name']
    search_help_text = _('Name')
    ordering = ['library__name', 'name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('library')

    def has_add_permission(self, request):
        return False


@admin.register(LibraryKeywordDocumentation)
class LibraryKeywordDocumentationAdmin(BaseDocumentationAdmin):
    pass
