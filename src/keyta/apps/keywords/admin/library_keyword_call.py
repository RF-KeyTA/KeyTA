from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import TabularInlineWithDelete
from keyta.widgets import BaseSelect, ModelSelect2AdminWidget

from ..forms import KeywordCallParameterFormset
from ..forms.keywordcall_parameter_formset import get_global_variables
from ..models import LibraryKeywordCall, KeywordCall, KeywordCallCondition, KeywordParameter
from .keywordcall import KeywordCallAdmin, KeywordDocField
from .keywordcall_parameters_inline import KeywordCallParametersInline


class LibraryKeywordCallParameterFormset(KeywordCallParameterFormset):
    def get_choices(self, kw_call: KeywordCall):
        if not kw_call.from_keyword.windows.count():
            system_ids = list(kw_call.from_keyword.systems.values_list('id', flat=True))
            return super().get_choices(kw_call) + get_global_variables(system_ids)

        return super().get_choices(kw_call)


class LibraryKeywordCallParametersInline(KeywordCallParametersInline):
    formset = LibraryKeywordCallParameterFormset


class ConditionsInline(TabularInlineWithDelete):
    model = KeywordCallCondition

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        kw_call: KeywordCall = obj
        kw_parameters = kw_call.from_keyword.parameters.all()

        formset.form.base_fields['keyword_parameter'].queryset = kw_parameters
        formset.form.base_fields['keyword_parameter'].widget = ModelSelect2AdminWidget(
            placeholder=_('Parameter auswählen'),
            model=KeywordParameter,
            search_fields=['name__icontains'],
        )
        formset.form.base_fields['condition'].widget = BaseSelect(
            _('Bedingung auswählen'),
            choices=formset.form.base_fields['condition'].widget.choices
        )
        formset.form.base_fields['expected_value'].help_text = _('Leeres Feld bedeutet Leerzeichen')

        return formset


@admin.register(LibraryKeywordCall)
class LibraryKeywordCallAdmin(
    KeywordDocField,
    KeywordCallAdmin
):
    parameters_inline = LibraryKeywordCallParametersInline

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return self.changeform_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def get_inlines(self, request, obj):
        return [ConditionsInline] + super().get_inlines(request, obj)
