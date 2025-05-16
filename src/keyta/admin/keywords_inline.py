from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.keywords.models import KeywordDocumentation
from keyta.widgets import open_link_in_modal


class Keywords(BaseTabularInline):
    model = KeywordDocumentation
    fields = ['name_link', 'short_doc']
    readonly_fields = ['name_link', 'short_doc']
    extra = 0
    can_delete = False
    verbose_name_plural = _('Schlüsselwörter')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description=_('Name'))
    def name_link(self, keyword: KeywordDocumentation):
        return open_link_in_modal(
            keyword.get_admin_url(),
            keyword.name
        )
