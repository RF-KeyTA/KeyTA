from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.widgets import KeywordCallSelect

from ..models import RobotKeywordCall
from .keywordcall import KeywordCallAdmin
from .keywordcall_return_value_inline import KeywordCallReturnValueInline


@admin.register(RobotKeywordCall)
class RobotKeywordCallAdmin(KeywordCallAdmin):
    fields = ['to_keyword_doc', 'condition']
    readonly_fields = ['to_keyword_doc']
    inlines = [KeywordCallReturnValueInline]

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

            field.widget = KeywordCallSelect(
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
                }
            )

        return field

    @admin.display(description=_('Schlüsselwort'))
    def to_keyword_doc(self, kw_call: RobotKeywordCall):
        return super().to_keyword_doc(kw_call)
