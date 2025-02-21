from django.utils.translation import gettext as _

from keyta.admin.base_inline import BaseTabularInline

from ..models import ResourceKeyword


class Keywords(BaseTabularInline):
    model = ResourceKeyword
    fields = ['name', 'short_doc']
    readonly_fields = ['name', 'short_doc']
    extra = 0
    can_delete = False
    show_change_link = True
    verbose_name_plural = _('Schlüsselwörter')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
