import re

from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from model_clone import CloneMixin

from keyta.apps.executions.models import Execution
from keyta.apps.libraries.models import Library, LibraryImport
from keyta.models.base_model import AbstractBaseModel
from keyta.models.documentation_mixin import DocumentationMixin
from keyta.rf_export.testcases import RFTestCase


class TestCase(DocumentationMixin, CloneMixin, AbstractBaseModel):
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

    _clone_linked_m2m_fields = ['systems']
    _clone_m2o_or_o2m_fields = ['steps']
    _clone_o2o_fields = ['execution']
    USE_UNIQUE_DUPLICATE_SUFFIX = False

    def __str__(self):
        return self.name

    def create_execution(self):
        library_ids = self.systems.values_list('library', flat=True).distinct()
        execution = Execution.objects.create(testcase=self)

        for library in Library.objects.filter(id__in=library_ids):
            LibraryImport.objects.create(
                execution=execution,
                library=library
            )

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

    def robot_documentation(self):
        return super().plaintext_documentation()

    def save(
        self, force_insert=False, force_update=False, using=None,
            update_fields=None
    ):
        self.name = re.sub(r"\s{2,}", ' ', self.name)
        super().save(force_insert, force_update, using, update_fields)

    def to_robot(self, get_variable_value, in_execution=False) -> RFTestCase:
        execute_from = 0

        if in_execution:
            if execute_step := self.steps.filter(execute=True).first():
                execute_from = execute_step.index

        test_steps = self.steps.filter(index__gte=execute_from).exclude(Q(to_keyword__isnull=True) | Q(enabled=False))

        return {
            'name': self.name,
            'doc': self.robot_documentation(),
            'steps': [
                test_step.to_robot(get_variable_value)
                for test_step in test_steps
            ]
        }

    class Meta:
        ordering = [Lower('name')]
        verbose_name = _('Testfall')
        verbose_name_plural = _('Testfälle')
