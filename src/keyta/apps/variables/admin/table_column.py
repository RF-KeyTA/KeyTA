from adminsortable2.admin import SortableAdminBase

from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_admin import BaseAdmin
from keyta.admin.base_inline import SortableTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.apps.keywords.models import KeywordCallParameter

from ..models import TableColumn, VariableValue


class Values(DeleteRelatedField, SortableTabularInline):
    model = VariableValue
    fields = ['value']
    verbose_name_plural = ''

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'value':
            field.widget = forms.TextInput(attrs={
                'style': 'width: 100%',
                'placeholder': _('Wert eintragen, anschließend Enter drücken')
            })

        return field


@admin.register(TableColumn)
class TableColumnAdmin(SortableAdminBase, BaseAdmin):
    def get_fields(self, request, obj=None):
        return []

    def get_inline_instances(self, request, obj=None):
        return [Values(self.model, self.admin_site)]

    def get_protected_objects(self, obj):
        table_column: TableColumn = obj

        return list(
            KeywordCallParameter.objects
            .filter(value_ref__table_column=table_column)
            .exclude(keyword_call__execution__isnull=False)
        )
