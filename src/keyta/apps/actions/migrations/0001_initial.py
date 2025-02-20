# Generated by Django 4.2.16 on 2024-11-28 09:02

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('libraries', '0001_initial'),
        ('executions', '0002_initial'),
        ('windows', '0001_initial'),
        ('keywords', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
            ],
            options={
                'verbose_name': 'Aktion',
                'verbose_name_plural': 'Aktionen',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('keywords.windowkeyword',),
        ),
        migrations.CreateModel(
            name='ActionExecution',
            fields=[
            ],
            options={
                'verbose_name': 'Ausführung',
                'verbose_name_plural': 'Ausführung',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('executions.keywordexecution',),
        ),
        migrations.CreateModel(
            name='ActionLibraryImport',
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
            name='RobotKeywordCall',
            fields=[
            ],
            options={
                'verbose_name': 'Schritt',
                'verbose_name_plural': 'Schritte',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('keywords.keywordcall',),
        ),
        migrations.CreateModel(
            name='ActionDocumentation',
            fields=[
            ],
            options={
                'verbose_name': 'Aktion Dokumentation',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('actions.action',),
        ),
    ]
