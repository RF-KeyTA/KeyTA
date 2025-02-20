# Generated by Django 4.2.17 on 2025-01-08 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('systems', '0002_alter_system_options_alter_system_attach_to_system_and_more'),
        ('windows', '0002_alter_window_options_and_more'),
        ('variables', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='variable',
            options={'verbose_name': 'Reference Value', 'verbose_name_plural': 'Reference Values'},
        ),
        migrations.AlterModelOptions(
            name='variablevalue',
            options={'verbose_name': 'Value', 'verbose_name_plural': 'Values'},
        ),
        migrations.AlterField(
            model_name='variable',
            name='all_windows',
            field=models.BooleanField(default=False, verbose_name='In all Windows'),
        ),
        migrations.AlterField(
            model_name='variable',
            name='description',
            field=models.CharField(blank=True, max_length=255, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='variable',
            name='setup_teardown',
            field=models.BooleanField(default=False, verbose_name='Setup/Teardown'),
        ),
        migrations.AlterField(
            model_name='variable',
            name='systems',
            field=models.ManyToManyField(blank=True, related_name='variables', to='systems.system', verbose_name='Systems'),
        ),
        migrations.AlterField(
            model_name='variable',
            name='windows',
            field=models.ManyToManyField(related_name='variables', to='windows.window', verbose_name='Windows'),
        ),
        migrations.AlterField(
            model_name='variablevalue',
            name='value',
            field=models.CharField(max_length=255, verbose_name='Value'),
        ),
    ]
