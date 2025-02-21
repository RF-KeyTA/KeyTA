from django.utils.translation import gettext as _

from keyta.admin.base_inline import BaseTabularInline

from ..forms import KeywordCallParameterFormset
from ..models import KeywordCallParameter


class KeywordCallParametersInline(BaseTabularInline):
    model = KeywordCallParameter
    fields = ['name', 'value']
    readonly_fields = ['name']
    formset = KeywordCallParameterFormset
    extra = 0
    max_num = 0
    can_delete = False

    def name(self, obj: KeywordCallParameter):
        return obj.name.replace('_', ' ').title()
