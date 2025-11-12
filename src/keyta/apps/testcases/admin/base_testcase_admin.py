from django.conf import settings
from django.contrib import admin
from django.contrib.admin.options import IncorrectLookupParameters
from django.core.exceptions import ValidationError
from django.db.models import Count, Q, QuerySet
from django.forms import ModelMultipleChoiceField
from django.http.request import HttpRequest
from django.http.response import HttpResponse
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
from keyta.apps.variables.models import VariableValue
from keyta.rf_export.rfgenerator import gen_testsuite
from keyta.rf_export.testsuite import RFTestSuite
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


def get_rf_testsuite(testcases: QuerySet, get_variable_value, user) -> RFTestSuite:
    testsuite = {
        'name': 'Testsuite',
        'settings': {
            'library_imports': {},
            'resource_imports': {},
            'suite_setup': None,
            'suite_teardown': None
        },
        'keywords': {},
        'testcases': []
    }

    for testcase in testcases.all():
        execution = TestCaseExecution.objects.get(testcase_id=testcase.id)
        rf_testsuite = execution.get_rf_testsuite(get_variable_value, user, {})
        testsuite['settings']['library_imports'].update(rf_testsuite['settings']['library_imports'])
        testsuite['settings']['resource_imports'].update(rf_testsuite['settings']['resource_imports'])
        testsuite['keywords'].update(rf_testsuite['keywords'])
        testsuite['testcases'].extend(rf_testsuite['testcases'])

    return testsuite


@admin.action(description=_('Ausgewählte Testfälle exportieren'))
def export_testcases(model_admin, request: HttpRequest, testcases: QuerySet):
    get_variable_value = lambda pk: VariableValue.objects.get(pk=pk).current_value
    testsuite = get_rf_testsuite(testcases, get_variable_value, request.user)
    robot_file = request.GET.get('testsuite', 'Testsuite') + '.robot'

    return HttpResponse(
        gen_testsuite(testsuite),
        headers={
            'Content-Type': 'text/plain',
            'Content-Disposition': f'attachment; filename="{robot_file}"'
        }
    )


class BaseTestCaseAdmin(DocumentationField, CloneModelAdminMixin, SortableAdminBase, BaseAdmin):
    actions = [export_testcases]
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
