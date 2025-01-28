import re
from abc import abstractmethod
from xml.etree import ElementTree

from django.db import models
from django.utils.translation import gettext as _

from apps.common.abc import AbstractBaseModel
from apps.executions.models import Execution, ExecutionLibraryImport
from apps.libraries.models import Library
from apps.rf_export.testcases import RFTestCase


class AbstractTestCase(AbstractBaseModel):
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

    def __str__(self):
        return self.name

    def create_execution(self):
        libraries = self.systems.values_list('library', flat=True).distinct()
        execution = Execution.objects.create(testcase=self)

        for library_id in libraries:
            ExecutionLibraryImport.objects.create(
                execution=execution,
                library=Library.objects.get(id=library_id)
            )

    @property
    def has_empty_sequence(self):
        return not self.steps.exists()

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

    def plaintext_documentation(self):
        doc = self.documentation.replace('&nbsp;', ' ')
        return''.join(ElementTree.XML('<doc>' + doc + '</doc>').itertext())

    @abstractmethod
    def robot_documentation(self):
        pass

    def save(
        self, force_insert=False, force_update=False, using=None,
            update_fields=None
    ):
        self.name = re.sub(r"\s{2,}", ' ', self.name)
        super().save(force_insert, force_update, using, update_fields)

    def to_robot(self) -> RFTestCase:
        return {
            'name': self.name,
            'doc': self.robot_documentation(),
            'steps': [
                test_step.to_robot()
                for test_step in self.steps.all()
                if test_step.enabled
            ]
        }

    class Meta:
        abstract = True
