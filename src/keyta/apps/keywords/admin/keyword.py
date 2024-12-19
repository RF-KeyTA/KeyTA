from django.contrib import admin
from django.db.models import QuerySet
from django.db.models.functions import Lower
from django.utils.translation import gettext as _

from adminsortable2.admin import SortableAdminBase
from django.http import HttpRequest

from apps.common.admin.base_admin import (
    BaseDocumentationAdmin,
    BaseAdminWithDoc
)
from ..models import KeywordDocumentation


class KeywordAdmin(SortableAdminBase, BaseAdminWithDoc):  # CloneModelAdminMixin
    list_display = ['name', 'short_doc']
    list_display_links = ['name']
    ordering = [Lower('name')]
    search_fields = ['name']
    search_help_text = _('Name')

    fields = ['name', 'short_doc']

    def get_fields(self, request: HttpRequest, obj=None):
        if request.user.is_superuser:
            return self.fields + ['documentation']
        else:
            return self.fields + ['read_documentation']

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        if request.user.is_superuser:
            return []
        else:
            return self.fields + ['read_documentation']


@admin.register(KeywordDocumentation)
class KeywordDocumentationAdmin(BaseDocumentationAdmin):
    pass
