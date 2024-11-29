from django.db import models

from apps.resources.models import ResourceImport, ResourceImportType


class ExecutionResourceImport(ResourceImport):
    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super().
                get_queryset()
                .only('execution', 'resource')
                .filter(type=ResourceImportType.FROM_EXECUTION)
                .order_by('resource__name')
            )

    objects = Manager()

    class Meta:
        proxy = True
        verbose_name = 'Ressource-Import'
        verbose_name_plural = 'Ressourcen-Imports'
