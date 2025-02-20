# Generated by Django 4.2.16 on 2024-11-28 09:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('windows', '0001_initial'),
        ('systems', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('description', models.CharField(blank=True, max_length=255, verbose_name='Beschreibung')),
                ('setup_teardown', models.BooleanField(default=False, verbose_name='Vor-/Nachbereitung')),
                ('all_windows', models.BooleanField(default=False, verbose_name='In allen Masken')),
                ('systems', models.ManyToManyField(blank=True, related_name='variables', to='systems.system', verbose_name='Systeme')),
                ('windows', models.ManyToManyField(related_name='variables', to='windows.window', verbose_name='Masken')),
            ],
            options={
                'verbose_name': 'Referenzwert',
                'verbose_name_plural': 'Referenzwerte',
            },
        ),
        migrations.CreateModel(
            name='VariableValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('value', models.CharField(max_length=255, verbose_name='Wert')),
                ('variable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='variables.variable')),
            ],
            options={
                'verbose_name': 'Wert',
                'verbose_name_plural': 'Werte',
            },
        ),
        migrations.AddConstraint(
            model_name='variablevalue',
            constraint=models.UniqueConstraint(fields=('variable', 'name'), name='unique_value_per_variable'),
        ),
    ]
