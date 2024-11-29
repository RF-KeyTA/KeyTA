from django.contrib import admin

from ..models import KeywordExecution
from .execution import ExecutionAdmin
from .keyword_execution_setup_inline import KeywordExecutionSetupInline
from .library_import_inline import LibraryImportsInline


@admin.register(KeywordExecution)
class KeywordExecutionAdmin(ExecutionAdmin):
    inlines = [
        LibraryImportsInline,
        KeywordExecutionSetupInline
    ]
