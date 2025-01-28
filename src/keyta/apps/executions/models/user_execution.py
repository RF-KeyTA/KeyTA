from pathlib import Path

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from keyta.models.base_model import AbstractBaseModel


class UserExecution(AbstractBaseModel):
    class Result(models.TextChoices):
        PASS = 'PASS', _('Erfolgreich')
        FAIL = 'FAIL', _('Fehlgeschlagen')

    execution = models.ForeignKey(
        'executions.Execution',
        on_delete=models.CASCADE,
        related_name='user_execs'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Benutzer')
    )
    result = models.CharField(
        max_length=255,
        choices=Result.choices,
        null=True,
        default=None,
        blank=True,
        verbose_name=_('Ergebnis')
    )
    log = models.CharField(
        max_length=255,
        null=True,
        default=None,
        blank=True,
        verbose_name=_('Protokoll')
    )
    running = models.BooleanField(default=False)

    def __str__(self):
        return str(self.execution)

    def save_execution_result(self, robot_result: dict):
        directory = Path('static') / 'execution_logs' / str(self.id)
        directory.mkdir(parents=True, exist_ok=True)
        log_html = directory / 'log.html'

        with open(log_html, 'w', encoding='utf-8') as file:
            file.write(robot_result['log'])

        self.log = str(log_html)
        self.result = robot_result['result']
        self.save()

    class Meta:
        verbose_name = _('Benutzer-bezogene Ausführung')
        verbose_name_plural = _('Benutzer-bezogene Ausführungen')
