import re
from pathlib import Path
from typing import Any
import unicodedata

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from keyta.apps.variables.models import VariableValue
from keyta.apps.executions.models import TestCaseExecution
from keyta.rf_export.rfgenerator import gen_testsuite


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.

    source: django.utils.text.slugify
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '_', value).strip('-_')


def write_file_to_disk(path, file_contents: str):
    with open(path, 'w', encoding='utf-8') as file_handle:
        file_handle.write(file_contents)


class Command(BaseCommand):
    help = """
    Exports all test cases as .robot files
    """

    def add_arguments(self, parser):
        pass

    def handle(self, *args: Any, **options: Any) -> None:
        get_variable_value = lambda pk: VariableValue.objects.get(pk=pk).current_value
        app, model = settings.AUTH_USER_MODEL.split('.')
        user_model = apps.get_model(app, model)
        user = user_model.objects.first()
        base_dir = Path('tests') / 'RF'
        base_dir.mkdir(parents=True, exist_ok=True)

        execution: TestCaseExecution
        for execution in TestCaseExecution.objects.all():
            testsuite = execution.get_rf_testsuite(get_variable_value, user, {})
            robot_file = slugify(testsuite['name']) + '.robot'
            write_file_to_disk(base_dir / robot_file, gen_testsuite(testsuite))
