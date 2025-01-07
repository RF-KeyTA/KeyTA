from django.contrib import admin
from django.db.models.functions import Lower
from django.utils.translation import gettext as _
from django.http import HttpRequest, HttpResponseRedirect

from adminsortable2.admin import SortableAdminBase

from apps.actions.models.action import Action
from apps.common.admin.base_admin import (
    BaseDocumentationAdmin,
    BaseAdminWithDoc
)
from apps.sequences.models.sequence import Sequence
from ..models import KeywordDocumentation, Keyword, KeywordType


@admin.register(Keyword)
class KeywordAdmin(SortableAdminBase, BaseAdminWithDoc):  # CloneModelAdminMixin
    list_display = ['name', 'short_doc']
    list_display_links = ['name']
    ordering = [Lower('name')]
    search_fields = ['name']
    search_help_text = _('Name')

    fields = ['name', 'short_doc']

    def change_view(self, request, object_id, form_url="", extra_context=None):
        keyword = Keyword.objects.get(pk=object_id)

        if keyword.type == KeywordType.ACTION:
            action = Action.objects.get(pk=object_id)
            return HttpResponseRedirect(action.get_admin_url())
        
        if keyword.type == KeywordType.SEQUENCE:
            sequence = Sequence.objects.get(pk=object_id)
            return HttpResponseRedirect(sequence.get_admin_url())
        
        return super().change_view(request, object_id, form_url, extra_context)

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
