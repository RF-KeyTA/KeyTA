import re

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, QuerySet
from django.utils.translation import gettext_lazy as _

from model_clone import CloneMixin
from taggit_selectize.managers import TaggableManager

from keyta.apps.executions.models import Execution, Setup
from keyta.apps.keywords.models import KeywordCallParameter
from keyta.apps.libraries.models import Library, LibraryImport
from keyta.apps.variables.models import Table
from keyta.models.base_model import AbstractBaseModel
from keyta.models.html2text import HTML2Text
from keyta.rf_export.testcases import RFTestCase


class TestCase(CloneMixin, AbstractBaseModel):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))
    documentation = models.TextField(blank=True, verbose_name=_('Dokumentation'))

    # Customization #
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Beschreibung')
    )
    systems = models.ManyToManyField(
        'systems.System',
        related_name='testcases',
        verbose_name=_('Systeme')
    )
    tags = TaggableManager(blank=True)

    _clone_linked_m2m_fields = ['systems']
    _clone_m2o_or_o2m_fields = ['steps']
    _clone_o2o_fields = ['execution']
    USE_UNIQUE_DUPLICATE_SUFFIX = False

    def __str__(self):
        return self.name

    def create_execution(self):
        library_ids = self.systems.values_list('library', flat=True).distinct()
        execution = Execution.objects.create(testcase=self)
        setup = Setup.objects.create(
            execution=execution,
            to_keyword=self.systems.first().attach_to_system,
            enabled=False
        )
        setup.index = 0
        setup.save()

        for library in Library.objects.filter(id__in=library_ids):
            LibraryImport.objects.create(
                execution=execution,
                library=library
            )

    def executable_steps(self, execution_state: dict) -> QuerySet:
        execute_from = self.steps.first().index
        execute_until = self.steps.last().index

        if begin_execution_index := execution_state.get('BEGIN_EXECUTION'):
            execute_from = begin_execution_index

        if end_execution_pk_index := execution_state.get('END_EXECUTION'):
            execute_until = end_execution_pk_index

        return (
            self.steps
            .prefetch_related('return_values')
            .prefetch_related('to_keyword')
            .filter(index__gte=execute_from)
            .filter(index__lte=execute_until)
            .exclude(Q(to_keyword__isnull=True) | Q(index__in=execution_state.get('SKIP_EXECUTION', [])))
        )

    def get_tables(self, user: AbstractUser):
        kw_call_params = (
            KeywordCallParameter.objects
            .filter(keyword_call__pk__in=self.steps.all())
            .filter(user=user)
            .filter(value_ref__isnull=False)
            .filter(value_ref__table_column__isnull=False)
        )
        tables: dict[int, Table] = {}

        param: KeywordCallParameter
        for param in kw_call_params:
            step = param.keyword_call
            column = param.value_ref.table_column
            tables[step.pk] = Table.objects.get(pk=column.table.pk)

        return tables

    @property
    def has_empty_sequence(self):
        return not self.steps.exists() or not self.steps.first().to_keyword

    @property
    def libraries(self):
        system_libraries = list(
            self.systems
            .values_list('system__library_id', flat=True)
        )
        window_libraries = list(
            self.steps
            .filter(window__libraries__library__isnull=False)
            .values_list('window__libraries__library_id', flat=True)
        )

        return set(system_libraries + window_libraries)

    def make_clone(self, attrs=None, sub_clone=False, using=None, parent=None):
        copies = self._meta.model.objects.filter(name__istartswith=self.name + _(' Kopie')).count()
        attrs = (attrs or {}) | {'name': self.name + _(' Kopie ') + str(copies+1)}

        return super().make_clone(attrs=attrs, sub_clone=sub_clone, using=using, parent=parent)

    def save(
        self, force_insert=False, force_update=False, using=None,
            update_fields=None
    ):
        self.name = re.sub(r"\s{2,}", ' ', self.name)
        super().save(force_insert, force_update, using, update_fields)

    def to_robot(self, user: AbstractUser, execution_state: dict, setup, teardown, stop_on_failure: bool, include_doc=False) -> RFTestCase:
        if include_doc:
            documentation = HTML2Text.parse(self.documentation)
        else:
            documentation = self.get_admin_url(absolute=True)

        row_variables = []
        table_columns: dict[int, list[str]] = {}
        table_variables: dict[int, tuple[str, list]] = {}

        table_pks = set()
        for step_pk, table in self.get_tables(user).items():
            if table.pk not in table_pks:
                table_pks.add(table.pk)
                table_columns[step_pk] = ['${%s}' % column for column in table.get_column_titles()]
                table_variable, table_row_variables = table.to_robot()
                row_variables.extend(table_row_variables)
                table_variables[step_pk] = table_variable

        def get_step_table(test_step_pk):
            if table_variable := table_variables.get(test_step_pk):
                table_name, _row_variables = table_variable
                return table_name, table_columns[test_step_pk]

            return None

        def teardown_disabled():
            return (
                execution_state.get('BEGIN_EXECUTION') or
                execution_state.get('END_EXECUTION') or
                not teardown.enabled
            )

        tags = list(self.tags.values_list('name', flat=True))

        if not stop_on_failure:
            tags.append('robot:recursive-continue-on-failure')

        return {
            'name': self.name,
            'doc': documentation,
            'tags': tags,
            'setup': setup.to_robot({}, user=user) if setup else None,
            'steps': [
                test_step.to_robot({}, table=get_step_table(test_step.pk), user=user)
                for test_step in self.executable_steps(execution_state)
            ],
            'teardown': teardown.to_robot({}, user=user) if teardown and not teardown_disabled() else None,
            'variables': [*row_variables, *list(table_variables.values())]
        }

    class Meta:
        verbose_name = _('Testfall')
        verbose_name_plural = _('Testfälle')
