import json

from django import forms
from django.utils.translation import gettext_lazy as _

from keyta.widgets import BaseSelect

from ..models import LibraryParameter, LibraryImportParameter


class LibraryParameterFormSet(forms.BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        # The index of extra forms is None
        if index is not None:
            kwarg: LibraryParameter = form.instance

            if isinstance(form.instance, LibraryImportParameter):
                kwarg: LibraryParameter = form.instance.library_parameter

            kwarg_type: list = json.loads(kwarg.typedoc)
            typedocs: dict = json.loads(kwarg.library.typedocs)
            choices = dict()
            user_input = False

            for type_ in kwarg_type:
                if type_ == 'bool':
                    choices['True'] = 'True'
                    choices['False'] = 'False'

                if any([
                    type_ in {'int', 'str', 'timedelta'},
                    type_.startswith('dict'),
                    type_.startswith('list')
                ]):
                    choices[kwarg.value] = kwarg.value
                    user_input = True

                if typedoc := typedocs.get(type_):
                    if typedoc['type'] == 'Enum':
                        for member in typedoc['members']:
                            if member.lower() not in {'true', 'false'}:
                                choices[member] = member

                    if typedoc['type'] == 'TypedDict':
                        user_input = True

            placeholder = _('Wert auswählen')

            if user_input:
                placeholder = _('Wert auswählen oder eintragen')

            form.fields['value'].widget = BaseSelect(
                placeholder,
                choices=choices.items(),
                attrs={
                    'data-tags': str(user_input).lower()
                }
            )
