import re

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, QuerySet
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from model_clone import CloneMixin
from taggit_selectize.managers import TaggableManager

from keyta.apps.executions.models import Execution, Setup
from keyta.apps.keywords.models import KeywordCallParameter, KeywordCallParameterSource
from keyta.apps.libraries.models import Library, LibraryImport
from keyta.apps.variables.models import Variable
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

    def get_tables_rows(self):
        table_variables = []
        row_variables = []

        value_ref_pks = (
            KeywordCallParameter.objects
            .filter(keyword_call__in=self.steps.all())
            .filter(value_ref__isnull=False)
            .values_list('value_ref', flat=True)
        )

        table_pks = (
            KeywordCallParameterSource.objects
            .filter(pk__in=value_ref_pks)
            .filter(table_column__isnull=False)
            .values_list('table_column__table', flat=True)
            .distinct()
        )

        for table in Variable.objects.filter(pk__in=table_pks):
            table_variable, table_row_variables = table.get_rows()
            table_variables.append(table_variable)
            row_variables.extend(table_row_variables)

        return table_variables, row_variables

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

    def to_robot(self, get_variable_value, user: AbstractUser, execution_state: dict, setup, teardown, include_doc=False) -> RFTestCase:
        if include_doc:
            documentation = HTML2Text.parse(self.documentation)
        else:
            documentation = self.get_admin_url(absolute=True) + '?steps_tab'

        tables, rows = self.get_tables_rows()

        def teardown_disabled():
            return (
                execution_state.get('BEGIN_EXECUTION') or
                execution_state.get('END_EXECUTION') or
                not teardown.enabled
            )

        return {
            'name': self.name,
            'doc': documentation,
            'setup': setup.to_robot(get_variable_value, user) if setup else None,
            'steps': [
                test_step.to_robot(get_variable_value, user=user)
                for test_step in self.executable_steps(execution_state)
            ],
            'teardown': teardown.to_robot(get_variable_value, user) if teardown and not teardown_disabled() else None,
            'variables': [*rows, *tables]
        }

    class Meta:
        ordering = [Lower('name')]
        verbose_name = _('Testfall')
        verbose_name_plural = _('Testfälle')
