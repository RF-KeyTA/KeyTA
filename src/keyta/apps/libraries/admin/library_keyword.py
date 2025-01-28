from django.contrib import admin
from django.db.models import Min
from django.db.models.functions import Lower
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseDocumentationAdmin

from apps.actions.models import RobotKeywordCall

from ..models import LibraryKeywordDocumentation, LibraryKeyword


class Uses(admin.TabularInline):
    fk_name = 'to_keyword'
    model = RobotKeywordCall
    fields = ['from_keyword']
    readonly_fields = ['from_keyword']
    extra = 0
    verbose_name_plural = _('Verwendungen')
    can_delete = False
    show_change_link = True

    def get_queryset(self, request):
        keyword_id = request.resolver_match.kwargs['object_id']

        queryset = (
            super(Uses, self)
            .get_queryset(request)
            .prefetch_related(*self.fields)
        )

        # Equivalent to
        # SELECT caller_id, MIN(id) AS first_call_id
        # FROM testcases.processcall
        # WHERE process_id=self.id
        # GROUP BY caller_id

        call_ids = list(
            first_call_id
            for _, first_call_id in
            queryset
            .filter(to_keyword_id__in=[keyword_id])
            .values_list('from_keyword_id')
            .annotate(first_call=Min('id'))
        )

        return (
            queryset
            .filter(id__in=call_ids)
            .order_by(Lower('from_keyword__name'))
        )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(LibraryKeyword)
class LibraryKeywordAdmin(BaseDocumentationAdmin):
    list_display = ['library', 'name', 'short_doc']
    list_filter = ['library']
    list_display_links = ['name']
    search_fields = ['name']
    search_help_text = _('Name')
    ordering = ['library__name', 'name']

    inlines = [
        # Uses
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('library')

    def has_add_permission(self, request):
        return False


@admin.register(LibraryKeywordDocumentation)
class LibraryKeywordDocumentationAdmin(BaseDocumentationAdmin):
    pass
