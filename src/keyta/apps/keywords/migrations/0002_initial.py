# Generated by Django 4.2.16 on 2024-11-28 09:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('variables', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('systems', '0001_initial'),
        ('libraries', '0001_initial'),
        ('windows', '0001_initial'),
        ('keywords', '0001_initial'),
        ('testcases', '0001_initial'),
        ('executions', '0002_initial'),
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='keywordcallparametersource',
            name='variable_value',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='variables.variablevalue'),
        ),
        migrations.AddField(
            model_name='keywordcallparameter',
            name='keyword_call',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameters', to='keywords.keywordcall'),
        ),
        migrations.AddField(
            model_name='keywordcallparameter',
            name='parameter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uses', to='keywords.keywordparameter'),
        ),
        migrations.AddField(
            model_name='keywordcallparameter',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='keywordcallparameter',
            name='value_ref',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='keywords.keywordcallparametersource'),
        ),
        migrations.AddField(
            model_name='keywordcall',
            name='execution',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='keyword_calls', to='executions.execution'),
        ),
        migrations.AddField(
            model_name='keywordcall',
            name='from_keyword',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='calls', to='keywords.keyword'),
        ),
        migrations.AddField(
            model_name='keywordcall',
            name='testcase',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='testcases.testcase'),
        ),
        migrations.AddField(
            model_name='keywordcall',
            name='to_keyword',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uses', to='keywords.keyword'),
        ),
        migrations.AddField(
            model_name='keywordcall',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='keywordcall',
            name='window',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='windows.window', verbose_name='Maske'),
        ),
        migrations.AddField(
            model_name='keyword',
            name='library',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='keywords', to='libraries.library', verbose_name='Bibliothek'),
        ),
        migrations.AddField(
            model_name='keyword',
            name='resource',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='keywords', to='resources.resource', verbose_name='Ressource'),
        ),
        migrations.AddField(
            model_name='keyword',
            name='systems',
            field=models.ManyToManyField(related_name='keywords', to='systems.system', verbose_name='Systeme'),
        ),
        migrations.AddField(
            model_name='keyword',
            name='windows',
            field=models.ManyToManyField(related_name='keywords', to='windows.window', verbose_name='Maske'),
        ),
        migrations.CreateModel(
            name='KeywordDocumentation',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('keywords.keyword',),
        ),
        migrations.AddConstraint(
            model_name='keywordparameter',
            constraint=models.UniqueConstraint(fields=('keyword', 'position'), name='unique_keyword_arg'),
        ),
        migrations.AddConstraint(
            model_name='keywordparameter',
            constraint=models.UniqueConstraint(fields=('keyword', 'name'), name='unique_keyword_kwarg'),
        ),
        migrations.AddConstraint(
            model_name='keywordparameter',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('type', 'ARG'), ('position__isnull', False)), models.Q(('type', 'KWARG'), ('position__isnull', True), ('default_value__isnull', False)), _connector='OR'), name='keyword_parameter_sum_type'),
        ),
        migrations.AddConstraint(
            model_name='keywordcallparametersource',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('type', 'KEYWORD_PARAMETER'), ('kw_param__isnull', False), ('kw_call_ret_val__isnull', True), ('variable_value__isnull', True)), models.Q(('type', 'KW_CALL_RETURN_VALUE'), ('kw_param__isnull', True), ('kw_call_ret_val__isnull', False), ('variable_value__isnull', True)), models.Q(('type', 'VARIABLE_VALUE'), ('kw_param__isnull', True), ('kw_call_ret_val__isnull', True), ('variable_value__isnull', False)), _connector='OR'), name='kw_call_parameter_source_sum_type'),
        ),
        migrations.AddConstraint(
            model_name='keywordcall',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('type', 'KEYWORD_CALL'), ('from_keyword__isnull', False), ('execution__isnull', True), ('testcase__isnull', True), ('window__isnull', True)), models.Q(('type', 'TEST_STEP'), ('testcase__isnull', False), ('window__isnull', False), ('execution__isnull', True), ('from_keyword__isnull', True)), models.Q(('type', 'KEYWORD_EXECUTION'), ('execution__isnull', False), ('from_keyword__isnull', True), ('testcase__isnull', True), ('window__isnull', True)), models.Q(('type', 'TEST_SETUP'), ('execution__isnull', False), ('from_keyword__isnull', True), ('testcase__isnull', True), ('window__isnull', True)), models.Q(('type', 'TEST_TEARDOWN'), ('execution__isnull', False), ('from_keyword__isnull', True), ('testcase__isnull', True), ('window__isnull', True)), models.Q(('type', 'SUITE_SETUP'), ('execution__isnull', False), ('from_keyword__isnull', True), ('testcase__isnull', True), ('window__isnull', True)), models.Q(('type', 'SUITE_TEARDOWN'), ('execution__isnull', False), ('from_keyword__isnull', True), ('testcase__isnull', True), ('window__isnull', True)), _connector='OR'), name='keyword_call_sum_type'),
        ),
        migrations.AddConstraint(
            model_name='keyword',
            constraint=models.UniqueConstraint(fields=('library', 'name'), name='unique_keyword_per_library'),
        ),
        migrations.AddConstraint(
            model_name='keyword',
            constraint=models.UniqueConstraint(fields=('resource', 'name'), name='unique_keyword_per_resource'),
        ),
        migrations.AddConstraint(
            model_name='keyword',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('type', 'LIBRARY'), ('library__isnull', False), ('resource__isnull', True)), models.Q(('type', 'RESOURCE'), ('resource__isnull', False), ('library__isnull', True)), models.Q(('type', 'ACTION'), ('library__isnull', True), ('resource__isnull', True)), models.Q(('type', 'SEQUENCE'), ('library__isnull', True), ('resource__isnull', True)), _connector='OR'), name='keyword_sum_type'),
        ),
    ]