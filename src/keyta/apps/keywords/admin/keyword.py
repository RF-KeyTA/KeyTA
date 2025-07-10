from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest, HttpResponseRedirect

from adminsortable2.admin import SortableAdminBase

from keyta.admin.base_admin import (
    BaseAdmin,
    BaseDocumentationAdmin
)
from keyta.admin.field_documentation import DocumentationField
from keyta.apps.actions.models import Action
from keyta.apps.sequences.models import Sequence

from ..models import KeywordDocumentation, Keyword
from ..models.keyword import KeywordType


def url_params(params: dict):
    return '&'.join([
        '%s=%s' % (name, value)
        for name, value in params.items()
    ])


@admin.register(Keyword)
class KeywordAdmin(DocumentationField, SortableAdminBase, BaseAdmin):
    list_display = ['name', 'short_doc']
    list_display_links = ['name']
    search_fields = ['name']
    search_help_text = _('Name')

    fields = ['name', 'short_doc']

    def change_view(self, request, object_id, form_url="", extra_context=None):
        keyword = Keyword.objects.get(pk=object_id)

        if keyword.resource:
            kw_doc = KeywordDocumentation.objects.get(pk=object_id)
            return HttpResponseRedirect(kw_doc.get_admin_url())

        if keyword.type == KeywordType.ACTION:
            action = Action.objects.get(pk=object_id)
            return HttpResponseRedirect(action.get_admin_url() + '?' + url_params(request.GET))
        
        if keyword.type == KeywordType.SEQUENCE:
            sequence = Sequence.objects.get(pk=object_id)
            return HttpResponseRedirect(sequence.get_admin_url() + '?' + url_params(request.GET))
        
        return super().change_view(request, object_id, form_url, extra_context)


class ArgsTableMixin:
    @admin.display(description=_('Parameters'))
    def args_table(self, keyword: Keyword):
        return mark_safe(keyword.args_doc)

    def get_fields(self, request: HttpRequest, obj=None):
        keyword: Keyword = obj
        
        if keyword.args_doc:
            return ['args_table'] + super().get_fields(request, obj)
        
        return super().get_fields(request, obj)

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        keyword: Keyword = obj

        if keyword.args_doc:
            return ['args_table'] + super().get_readonly_fields(request, obj)
        
        return super().get_readonly_fields(request, obj)


@admin.register(KeywordDocumentation)
class KeywordDocumentationAdmin(
    ArgsTableMixin,
    BaseDocumentationAdmin
):
    pass
