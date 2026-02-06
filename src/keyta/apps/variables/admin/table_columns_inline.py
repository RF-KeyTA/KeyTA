from django import forms
from django.conf import settings
from django.contrib import admin
from django.forms.utils import ErrorDict, ErrorList
from django.utils.translation import gettext_lazy as _

from adminsortable2.admin import CustomInlineFormSet

from keyta.admin.base_inline import SortableTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.widgets import open_link_in_modal, Icon

from ..models import TableColumn, Variable


class TableColumnsFormset(CustomInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variable: Variable = kwargs.get('instance')

    def clean(self):
        for form in self.extra_forms:
            name = form.cleaned_data.get('name')

            if name and self.variable.columns.filter(name=name).exists():
                form._errors = ErrorDict()
                form._errors['name'] = ErrorList([
                    _('Die Tabelle enthält bereits eine Spalte mit diesem Namen.')
                ])


class TableColumns(DeleteRelatedField, SortableTabularInline):
    model = TableColumn
    fields = ['name', 'column_values']
    formset = TableColumnsFormset
    readonly_fields = ['column_values']
    verbose_name = _('Spalte')
    verbose_name_plural = _('Spalten')

    @admin.display(description=_('Werte'))
    def column_values(self, obj):
        column: TableColumn = obj

        if not column.pk:
            return '-'

        return open_link_in_modal(
            column.get_admin_url(),
            str(Icon(settings.FA_ICONS.column_values))
        )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'name':
            field.widget = forms.TextInput(attrs={
                'style': 'width: 100%',
                'placeholder': _('Name eintragen, anschließend Enter drücken')
            })

        return field

    # Sortable inlines need change permission
    def has_change_permission(self, request, obj=None) -> bool:
        return True
