from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.widgets import KeywordCallParameterSelect

from ..forms import KeywordCallParameterFormset
from ..forms.keywordcall_parameter_formset import get_global_variables
from ..models import LibraryKeywordCall, KeywordCall
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


@admin.register(LibraryKeywordCall)
class LibraryKeywordCallAdmin(
    KeywordDocField,
    KeywordCallAdmin
):
    parameters_inline = LibraryKeywordCallParametersInline

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return self.changeform_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj) + ['condition']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'condition':
            kw_call_id = request.resolver_match.kwargs['object_id']
            kw_call: LibraryKeywordCall = LibraryKeywordCall.objects.get(pk=kw_call_id)
            keyword_params = list(kw_call.from_keyword.parameters.values_list('name', flat=True))
            return_values = list(kw_call.get_previous_return_values().values_list('name', flat=True))

            kw_parameters = []

            if keyword_params:
                kw_parameters = [[
                    _('Parameters'),
                    [
                        (name, name)
                        for name in
                        keyword_params
                    ]
                ]]

            prev_return_values = []

            if return_values:
                prev_return_values = [[
                    _('Rückgabewerte'),
                    [
                        (return_value, return_value)
                        for return_value in
                        return_values
                    ]
                ]]

            user_input = [[
                _('Eingabe'),
                [
                    (kw_call.condition or None, kw_call.condition or _('Kein Wert'))
                ]
            ]]

            field.widget = KeywordCallParameterSelect(
                _('Bedingung eintragen'),
                choices=(
                    [(None, '')] +
                    user_input +
                    kw_parameters +
                    prev_return_values
                ),
                attrs={
                    # Allow manual input
                    'data-tags': 'true',
                    # Allow clearing the field
                    'data-allow-clear': 'true',
                }
            )

        return field
