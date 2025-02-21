from django.utils.translation import gettext as _

from keyta.admin.base_inline import BaseTabularInline

from ..models import KeywordCallReturnValue


class KeywordCallReturnValueInline(BaseTabularInline):
    model = KeywordCallReturnValue
    fields = ['name']
    extra = 1
    max_num = 1
    verbose_name = _('Rückgabewert')
    verbose_name_plural = _('Rückgabewert')
    can_delete = False
