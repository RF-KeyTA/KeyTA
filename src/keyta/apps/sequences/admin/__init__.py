from django.apps import apps

from .action_call import ActionCallAdmin
from .sequence import SequenceAdmin, SequenceDocumentationAdmin, WindowSequenceAdmin

if apps.is_installed('keyta.apps.resources'):
    from .resource_import import SequenceResourceImportAdmin
