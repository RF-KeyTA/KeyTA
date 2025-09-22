from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect

from adminsortable2.admin import SortableAdminBase

from keyta.admin.base_admin import BaseAdmin
from keyta.admin.field_documentation import DocumentationField
from keyta.apps.actions.models import Action
from keyta.apps.sequences.models import Sequence
from keyta.widgets import url_query_parameters

from ..models import KeywordDocumentation, Keyword
from ..models.keyword import KeywordType


@admin.register(Keyword)
class KeywordAdmin(DocumentationField, SortableAdminBase, BaseAdmin):
    list_display = ['name', 'window_list']
    list_display_links = ['name']
    search_fields = ['name']
    search_help_text = _('Name')

    @admin.display(description=_('Masken'))
    def window_list(self, obj):
        keyword: Keyword = obj

        return ', '.join(keyword.windows.values_list('name', flat=True))

    fields = ['name', 'short_doc']

    def change_view(self, request, object_id, form_url="", extra_context=None):
        keyword = Keyword.objects.get(pk=object_id)

        if keyword.resource:
            kw_doc = KeywordDocumentation.objects.get(pk=object_id)
            return HttpResponseRedirect(kw_doc.get_admin_url())

        if keyword.type == KeywordType.ACTION:
            action = Action.objects.get(pk=object_id)
            return HttpResponseRedirect(action.get_admin_url() + '?' + url_query_parameters(request.GET))
        
        if keyword.type == KeywordType.SEQUENCE:
            sequence = Sequence.objects.get(pk=object_id)
            return HttpResponseRedirect(sequence.get_admin_url() + '?' + url_query_parameters(request.GET))
        
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(KeywordDocumentation)
class KeywordDocumentationAdmin(
    admin.ModelAdmin
):
    fields = ['html_doc']
    readonly_fields = ['html_doc']

    @admin.display(description='')
    def html_doc(self, keyword: Keyword):
        return mark_safe(keyword.documentation)
