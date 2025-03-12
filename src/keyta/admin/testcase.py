from django.db.models.functions import Lower
from django.utils.translation import gettext as _

from adminsortable2.admin import SortableAdminBase
from model_clone import CloneModelAdminMixin

from keyta.apps.executions.admin import ExecutionInline
from keyta.apps.executions.models import TestCaseExecution
from keyta.apps.keywords.admin import TestStepsInline
from keyta.models.testcase import AbstractTestCase
from keyta.widgets import BaseSelectMultiple

from .base_admin import BaseAdmin
from .list_filters import SystemListFilter


class LocalExecution(ExecutionInline):
    model = TestCaseExecution


class BaseTestCaseAdmin(CloneModelAdminMixin, SortableAdminBase, BaseAdmin):
    list_display = ['name', 'description']
    list_display_links = ['name']
    list_filter = [
        ('systems', SystemListFilter),
    ]
    search_fields = ['name']
    search_help_text = _('Name')
    ordering = [Lower('name')]

    fields = [
        'systems',
        'name',
        'description',
        'documentation'
    ]
    inlines = [
        TestStepsInline,
        LocalExecution
    ]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'systems':
            field.widget = BaseSelectMultiple(_('Systeme hinzufügen'))

        return field

    def get_inlines(self, request, obj):
        testcase: AbstractTestCase = obj

        if not testcase:
            return []

        if testcase.has_empty_sequence:
            return [TestStepsInline]

        return self.inlines

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        testcase: AbstractTestCase = obj

        if not change:
            form.save_m2m()
            testcase.create_execution()
