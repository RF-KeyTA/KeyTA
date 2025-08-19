from django.utils.translation import gettext_lazy as _

from keyta.widgets import BaseSelect

from ..json_value import JSONValue
from ..models import KeywordCall, KeywordCallParameter
from .keywordcall_parameter_formset import (
    get_keyword_parameters,
    get_prev_return_values,
    get_global_variables
)
from .user_input_formset import DynamicChoiceField, UserInputFormset, invert_dictionary, user_input_field


class LibraryKeywordCallParameterFormset(UserInputFormset):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        # The index of extra forms is None
        if index is None:
            return

        user_input = self.get_user_input(form, index)
        form.fields['value'] = user_input_field(
            _('Wert auswählen oder eintragen'),
            user_input,
            choices=self.ref_choices
        )

        kw_call_parameter: KeywordCallParameter = form.instance
        if kw_call_parameter.pk:
            if type_list := kw_call_parameter.parameter.get_typedoc():
                if type_list == ['bool']:
                    choices = [
                        (JSONValue.user_input('True'), 'True'),
                        (JSONValue.user_input('False'), 'False'),
                    ]

                    form.fields['value'] = DynamicChoiceField(
                        widget=BaseSelect(
                            '',
                            choices=choices + get_keyword_parameters(kw_call_parameter.keyword_call)
                        )
                    )
                else:
                    choices = dict()
                    enable_user_input = False

                    for type_ in type_list:
                        if type_ == 'None':
                            choices['None'] = [
                                (JSONValue.user_input('None'), 'None')
                            ]
                        elif type_ == 'bool':
                            choices['bool'] = [
                                (JSONValue.user_input('True'), 'True'),
                                (JSONValue.user_input('False'), 'False'),
                            ]
                        elif type_ in self.typedocs:
                            typedoc = self.typedocs[type_]

                            if typedoc['type'] == 'Enum':
                                enum_name = typedoc['name']
                                choices[enum_name] = dict()

                                sorted_members = sorted(typedoc['items'])
                                members = (
                                    list(filter(lambda x: x[0].isalpha(), sorted_members)) +
                                    list(filter(lambda x: not x[0].isalpha(), sorted_members))
                                )
                                for member in members:
                                    if member.lower() not in {'true', 'false'}:
                                        choices[enum_name][JSONValue.user_input(member)] = member

                                choices[enum_name] = list(choices[enum_name].items())
                            else:
                                enable_user_input = True
                        else:
                            enable_user_input = True

                    if enable_user_input:
                        if choices:
                            enum_values = {
                                key
                                for value in list(choices.values())
                                for key in invert_dictionary(dict(value))
                            }
                            json_value, value = user_input

                            if value in enum_values:
                                user_input = None, _('Kein Wert')

                        form.fields['value'] = user_input_field(
                            _('Wert auswählen oder eintragen'),
                            user_input,
                            choices=list(choices.items()) + self.ref_choices
                        )
                    else:
                        if choices:
                            form.fields['value'] = DynamicChoiceField(
                                widget=BaseSelect(
                                    '',
                                    choices=list(choices.items())
                                )
                            )

    def get_ref_choices(self, kw_call: KeywordCall):
        ref_choices = get_keyword_parameters(kw_call) + get_prev_return_values(kw_call)

        if not kw_call.from_keyword.windows.count():
            system_ids = list(kw_call.from_keyword.systems.values_list('id', flat=True))

            return ref_choices + get_global_variables(system_ids)

        return ref_choices

    def get_json_value(self, form):
        kw_call_parameter: KeywordCallParameter = form.instance
        return kw_call_parameter.json_value
