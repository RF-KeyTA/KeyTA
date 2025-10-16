from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.testcases.models import TestStep


class UsesInline(BaseTabularInline):
    model = TestStep
    fk_name = 'to_keyword'
    fields = ['testcase']
    verbose_name_plural = _('Verwendungen')

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False
