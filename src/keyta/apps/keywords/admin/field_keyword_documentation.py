from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.widgets import open_link_in_modal

from ..models import KeywordCall, KeywordDocumentation


class KeywordDocField:
    @admin.display(description=_('Dokumentation'))
    def to_keyword_doc(self, kw_call: KeywordCall):
        keyword_doc = KeywordDocumentation.objects.get(pk=kw_call.to_keyword.pk)

        return open_link_in_modal(
            keyword_doc.get_admin_url(),
            str(keyword_doc)
        )

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj) + ['to_keyword_doc']

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj) + ['to_keyword_doc']
