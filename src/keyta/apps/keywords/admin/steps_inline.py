from django.utils.translation import gettext as _

from keyta.admin.base_inline import DeleteRelatedField, SortableTabularInline


from ..forms import StepsForm
from ..models import KeywordCall
from .field_first_parameter import FirstParameterField
from .field_keywordcall_args import KeywordCallArgsField


class StepsInline(
    DeleteRelatedField,
    FirstParameterField, 
    KeywordCallArgsField, 
    SortableTabularInline
):
    model = KeywordCall
    fk_name = 'from_keyword'
    fields = ['to_keyword']
    form = StepsForm
    extra = 1  # Must be > 0 in order for django-select2 to work
