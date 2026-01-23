from django import forms
from django.utils.translation import gettext_lazy as _

from keyta.widgets import BaseSelect

from ..models import LibraryParameter, LibraryImportParameter


class LibraryParameterFormSet(forms.BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        import_param = None
        library_parameter: LibraryParameter = form.instance

        if isinstance(form.instance, LibraryImportParameter) and form.instance.pk:
            import_param = form.instance
            library_parameter: LibraryParameter = import_param.library_parameter

        if library_parameter.pk:
            choices = []
            enable_user_input = False
            typedocs = library_parameter.library.get_typedocs()

            if type_list := library_parameter.get_typedoc():
                if type_list == ['bool']:
                    choices.extend([
                        ('True', 'True'),
                        ('False', 'False')
                    ])
                else:
                    for type_ in type_list:
                        if type_ == 'None':
                            choices.append(('${None}', 'None'))
                        elif type_ == 'bool':
                            choices.extend([
                                ('True', 'True'),
                                ('False', 'False')
                            ])
                        elif type_ in typedocs:
                            typedoc = typedocs[type_]

                            if typedoc['type'] == 'Enum':
                                for item in typedoc['items']:
                                    if item.lower() not in {'true', 'false'}:
                                        choices.append((item, item))
                            else:
                                enable_user_input = True
                        else:
                            enable_user_input = True

            if enable_user_input:
                if import_param:
                    user_input = import_param.value, import_param.value
                else:
                    user_input = library_parameter.value, library_parameter.value

                if user_input == ('${None}', '${None}'):
                    user_input = ('${None}', 'None')

                if user_input in set(choices):
                    user_input = None, _('Kein Wert')

                form.fields['value'].widget = BaseSelect(
                    '',
                    choices=(
                        [(_('Eingabe'), [user_input])] +
                        choices
                    ),
                    attrs={
                        'data-tags': 'true'
                    }
                )
            else:
                form.fields['value'].widget = BaseSelect(
                    '',
                    choices=choices
                )
