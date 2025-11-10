from django.conf import settings
from django.contrib import admin
from django.contrib.admin.options import IncorrectLookupParameters
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.forms import ModelMultipleChoiceField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from adminsortable2.admin import SortableAdminBase
from model_clone import CloneModelAdminMixin

from keyta.admin.base_admin import BaseAdmin
from keyta.admin.field_documentation import DocumentationField
from keyta.admin.list_filters import SystemListFilter
from keyta.apps.executions.admin import ExecutionInline
from keyta.apps.executions.models import TestCaseExecution
from keyta.apps.systems.models import System
from keyta.widgets import CheckboxSelectMultipleSystems, Icon

from ..models import TestCase
from .test_steps_inline import TestStepsInline


class LocalExecution(ExecutionInline):
    model = TestCaseExecution


class TagFilter(admin.RelatedFieldListFilter):
    template = 'tag_filter.html'

    @property
    def include_empty_choice(self):
        return False

    def queryset(self, request, queryset):
        try:
            if self.lookup_val_isnull:
                return queryset.filter(**{self.lookup_kwarg_isnull: True})

            choices = self.lookup_val
            if not choices:
                return queryset

            choice_len = len(choices)

            queryset = queryset.alias(
                nmatch=Count(self.field_path, filter=Q(**{'tags__id__in': choices}), distinct=True)
            ).filter(nmatch=choice_len)

            return queryset

        except (ValueError, ValidationError) as e:
            raise IncorrectLookupParameters(e)


class BaseTestCaseAdmin(DocumentationField, CloneModelAdminMixin, SortableAdminBase, BaseAdmin):
    change_list_template = 'testcase_change_list.html'
    list_display = ['execute', 'name', 'description']
    list_display_links = ['name']
    list_filter = [
        ('systems', SystemListFilter),
        ('tags', TagFilter)
    ]
    search_fields = ['name']
    search_help_text = _('Name')

    @admin.display(description=mark_safe('<span title="%s" style="cursor: default">▶</span>' % _("Ausführung")))
    def execute(self, obj):
        testcase: TestCase = obj
        execution = TestCaseExecution.objects.get(testcase=testcase)
        url = execution.get_admin_url() + '?start'
        title = str(Icon(settings.FA_ICONS.exec_start, styles={'font-size': '18px'}))

        return mark_safe(f'<a href="%s" id="exec-btn-{testcase.pk}">%s</a>' % (url, title))

    fields = [
        'systems',
        'tags',
        'name',
        'description',
    ]
    inlines = [
        TestStepsInline,
        LocalExecution
    ]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'systems':
            field = ModelMultipleChoiceField(
                widget=CheckboxSelectMultipleSystems,
                queryset=field.queryset
            )
            if System.objects.count() == 1:
                field.initial = [System.objects.first()]
            field.label = _('Systeme')

            if testcase_id := request.resolver_match.kwargs.get('object_id'):
                testcase = TestCase.objects.get(id=testcase_id)
                testcase_systems = testcase.systems.values_list('pk', flat=True)
                teststep_systems = testcase.steps.values_list('window__systems', flat=True)
                field.widget.in_use = set(testcase_systems).intersection(teststep_systems)

        return field

    def get_inlines(self, request, obj):
        testcase: TestCase = obj

        if not testcase:
            return []

        if testcase.has_empty_sequence:
            return [TestStepsInline]

        return self.inlines

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        testcase: TestCase = obj

        if not change:
            form.save_m2m()
            testcase.create_execution()
