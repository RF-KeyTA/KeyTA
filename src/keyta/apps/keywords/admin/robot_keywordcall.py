from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.widgets import KeywordCallParameterSelect

from ..models import RobotKeywordCall
from .keywordcall import KeywordCallAdmin, KeywordDocField


@admin.register(RobotKeywordCall)
class RobotKeywordCallAdmin(
    KeywordDocField,
    KeywordCallAdmin
):
    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj) + ['condition']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'condition':
            kw_call_id = request.resolver_match.kwargs['object_id']
            kw_call: RobotKeywordCall = RobotKeywordCall.objects.get(pk=kw_call_id)
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
