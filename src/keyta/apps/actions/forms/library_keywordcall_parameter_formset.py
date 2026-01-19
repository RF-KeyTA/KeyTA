from django.utils.translation import gettext_lazy as _

from keyta.widgets import BaseSelect

from keyta.apps.keywords.json_value import JSONValue
from keyta.apps.keywords.models import KeywordCall, KeywordCallParameter
from keyta.apps.keywords.forms.keywordcall_parameter_formset import (
    KeywordCallParameterFormset,
    get_global_variables,
    get_keyword_parameters
)
from keyta.apps.keywords.forms.user_input_formset import DynamicChoiceField, invert_dictionary, user_input_field


class LibraryKeywordCallParameterFormset(KeywordCallParameterFormset):
    def add_fields(self, form, index):
        super().add_fields(form, index)

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
                                (JSONValue.user_input('${None}'), 'None')
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
                        user_input = self.get_user_input(form, index)

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
        ref_choices = super().get_ref_choices(kw_call)

        if not kw_call.from_keyword.windows.count():
            system_ids = list(kw_call.from_keyword.systems.values_list('id', flat=True))

            return ref_choices + get_global_variables(system_ids)

        return ref_choices
