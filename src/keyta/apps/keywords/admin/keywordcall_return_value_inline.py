from django.utils.translation import gettext as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField

from ..models import KeywordCallReturnValue


class KeywordCallReturnValueInline(DeleteRelatedField, BaseTabularInline):
    model = KeywordCallReturnValue
    fields = ['name']
    extra = 0
    verbose_name = _('Rückgabewert')
    verbose_name_plural = _('Rückgabewerte')
    can_delete = False
