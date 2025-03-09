from adminsortable2.admin import CustomInlineFormSet

from keyta.admin.base_inline import DeleteRelatedField, SortableTabularInline

from ..forms import StepsForm
from ..models import KeywordCall
from .field_first_parameter import FirstParameterField
from .field_keywordcall_args import KeywordCallArgsField


class StepsFormset(CustomInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        kw_call: KeywordCall = form.instance

        # The index of an extra form is None
        if index is not None and kw_call.pk:
            # A keyword from a Resource cannot be edited
            if kw_call.to_keyword.resource:
                form.fields['to_keyword'].widget.can_change_related = False


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
    formset = StepsFormset
    extra = 0
