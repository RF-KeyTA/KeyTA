# Generated by Django 4.2.16 on 2024-11-28 09:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libraries', '0001_initial'),
        ('executions', '0001_initial'),
        ('keywords', '0001_initial'),
        ('testcases', '0001_initial'),
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExecutionLibraryImport',
            fields=[
            ],
            options={
                'verbose_name': 'Bibliothek-Import',
                'verbose_name_plural': 'Bibliothek-Imports',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('libraries.libraryimport',),
        ),
        migrations.CreateModel(
            name='ExecutionResourceImport',
            fields=[
            ],
            options={
                'verbose_name': 'Ressource-Import',
                'verbose_name_plural': 'Ressourcen-Imports',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('resources.resourceimport',),
        ),
        migrations.CreateModel(
            name='KeywordExecutionCall',
            fields=[
            ],
            options={
                'verbose_name': 'Aufrufparameter',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('keywords.keywordcall',),
        ),
        migrations.CreateModel(
            name='SetupTeardown',
            fields=[
            ],
            options={
                'verbose_name': 'Vor-/Nachbereitung',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('keywords.keywordcall',),
        ),
        migrations.AddField(
            model_name='userexecution',
            name='execution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_execs', to='executions.execution'),
        ),
        migrations.AddField(
            model_name='userexecution',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Benutzer'),
        ),
        migrations.AddField(
            model_name='execution',
            name='keyword',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='execution', to='keywords.keyword'),
        ),
        migrations.AddField(
            model_name='execution',
            name='testcase',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='execution', to='testcases.testcase'),
        ),
        migrations.CreateModel(
            name='KeywordExecution',
            fields=[
            ],
            options={
                'verbose_name': 'Ausführung',
                'verbose_name_plural': 'Ausführung',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('executions.execution',),
        ),
        migrations.CreateModel(
            name='KeywordExecutionSetup',
            fields=[
            ],
            options={
                'verbose_name': 'Schlüsselwort-Aufruf',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('executions.setupteardown',),
        ),
        migrations.CreateModel(
            name='TestCaseExecutionSetupTeardown',
            fields=[
            ],
            options={
                'verbose_name': 'Schlüsselwort-Aufruf',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('executions.setupteardown',),
        ),
        migrations.AddConstraint(
            model_name='execution',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('type', 'KEYWORD_EXECUTION'), ('keyword__isnull', False), ('testcase__isnull', True)), models.Q(('type', 'TESTCASE_EXECUTION'), ('keyword__isnull', True), ('testcase__isnull', False)), _connector='OR'), name='execution_sum_type'),
        ),
    ]
