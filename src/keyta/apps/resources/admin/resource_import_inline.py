from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline

from ..models import ResourceImport


class ResourceImportsInline(BaseTabularInline):
    model = ResourceImport
    fields = ['resource']
    extra = 0
    max_num = 0
    can_delete = False
    verbose_name = _('Ressource')
    verbose_name_plural = _('Ressourcen')


    def has_change_permission(self, request, obj=None) -> bool:
        return False
