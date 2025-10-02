import re
from collections import defaultdict

from django.db.models import QuerySet
from django.forms.utils import ErrorDict, ErrorList
from django.utils.translation import gettext_lazy as _

from keyta.apps.variables.models import Variable, VariableValue

from ..json_value import JSONValue
from ..models import (
    KeywordCall,
    KeywordCallParameterSource,
    KeywordCallParameter,
    KeywordCallReturnValue
)
from .user_input_formset import UserInputFormset, user_input_field


def get_global_variables(system_ids: list[int]):
    variables = Variable.objects.filter(
        systems__in=system_ids,
        windows__isnull=True
    ).distinct()

    return get_variables_choices(variables)


def get_keyword_parameters(kw_call: KeywordCall):
    if not kw_call.from_keyword or not kw_call.from_keyword.parameters.exists():
        return []

    return [[
        _('Parameters'),
        [
            (source.get_value().jsonify(), str(source))
            for source in KeywordCallParameterSource.objects
            .filter(kw_param__keyword=kw_call.from_keyword)
        ]
    ]]


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=lambda x: alphanum_key(unrobot(x[1])))


def unrobot(token):
    dict_access = re.compile(r'\${(.*)}\[(.*)\]')

    if match := re.match(dict_access, token):
        return f'{match.group(1)}.{match.group(2)}'

    return token


def get_prev_return_values(kw_call: KeywordCall):
    prev_return_values = kw_call.get_previous_return_values()

    if not prev_return_values.exists():
        return []

    return_value_keys = []
    return_value_refs = []

    return_value: KeywordCallReturnValue
    for return_value in prev_return_values:
        if typedoc := return_value.typedoc:
            for key in typedoc['keys']:
                value = '${%s}[%s]' % (str(return_value), key)
                json_value = JSONValue(
                    arg_name=None,
                    kw_call_index=None,
                    pk=None,
                    user_input=value
                ).jsonify()
                return_value_keys.append((json_value, value))
        else:
            return_value_refs.append(return_value)

    sources = KeywordCallParameterSource.objects.filter(
        kw_call_ret_val__in=return_value_refs
    )

    return [[
        _('Vorherige Rückgabewerte'),
        # Sort the return values by their string representation
        natural_sort(
            return_value_keys +
            [
                (source.get_value().jsonify(), str(source))
                for source in sources
            ]
        )
    ]]


def get_variables_choices(variables: QuerySet):
    grouped_variable_values = defaultdict(list)
    variable_names = (
        VariableValue.objects
        .filter(variable__in=variables)
        .values_list('variable__name', flat=True)
    )
    variable_value_sources = (
        KeywordCallParameterSource.objects
        .filter(variable_value__variable__in=variables)
    )

    for variable_name, source in zip(variable_names, variable_value_sources):
        grouped_variable_values[variable_name].append((source.get_value().jsonify(), str(source)))

    return [
        [
            variable,
            values
        ]
        for variable, values in sorted(grouped_variable_values.items(), key=lambda kv: kv[0].lower())
    ]


class ErrorsMixin:
    def add_fields(self, form, index):
        super().add_fields(form, index)

        if index is not None:
            json_value = self.get_json_value(form)

            if not json_value.user_input and not json_value.pk:
                form._errors = ErrorDict()
                form._errors['value'] = ErrorList([
                    form.fields['value'].default_error_messages['required']
                ])

    # This is necessary in order to be able to save the formset
    # despite the errors that were added in form._errors
    def is_valid(self):
        return True


class KeywordCallParameterFormset(UserInputFormset):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        # The index of extra forms is None
        if index is None:
            return

        form.fields['value'] = user_input_field(
            _('Wert auswählen oder eintragen'),
            self.get_user_input(form, index),
            choices=self.ref_choices
        )

    def get_ref_choices(self, kw_call: KeywordCall):
        return get_keyword_parameters(kw_call) + get_prev_return_values(kw_call)

    def get_json_value(self, form):
        kw_call_parameter: KeywordCallParameter = form.instance
        return kw_call_parameter.json_value


class KeywordCallParameterFormsetWithErrors(ErrorsMixin, KeywordCallParameterFormset):
    pass
