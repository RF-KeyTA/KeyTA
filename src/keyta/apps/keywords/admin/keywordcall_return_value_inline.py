from django.contrib import admin
from django.utils.translation import gettext as _

from ..models import KeywordCallReturnValue


class KeywordCallReturnValueInline(admin.TabularInline):
    model = KeywordCallReturnValue
    fields = ['name']
    extra = 1
    max_num = 1
    verbose_name = _('Rückgabewert')
    verbose_name_plural = _('Rückgabewert')
    can_delete = False
