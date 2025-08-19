import json

from django import forms

from keyta.widgets import BaseSelect

from ..models import LibraryParameter, LibraryImportParameter


class LibraryParameterFormSet(forms.BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        # The index of extra forms is None
        if index is not None:
            import_param = None
            kwarg: LibraryParameter = form.instance

            if isinstance(form.instance, LibraryImportParameter):
                import_param = form.instance
                kwarg: LibraryParameter = import_param.library_parameter

            kwarg_type: list = json.loads(kwarg.typedoc)
            typedocs: dict = json.loads(kwarg.library.typedocs)
            typedocs = kwarg.library.get_typedocs()
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
                    if import_param:
                        choices[import_param.value] = import_param.value
                    else:
                        choices[kwarg.value] = kwarg.value
                    user_input = True

                if type_ in typedocs:
                    typedoc = typedocs[type_]
                    if typedoc['type'] == 'Enum':
                        for item in typedoc['items']:
                            if item.lower() not in {'true', 'false'}:
                                choices[item] = item

                    if typedoc['type'] == 'TypedDict':
                        user_input = True

            form.fields['value'].widget = BaseSelect(
                '',
                choices=choices.items(),
                attrs={
                    'data-tags': str(user_input).lower()
                }
            )
