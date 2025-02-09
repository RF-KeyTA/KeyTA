# Generated by Django 4.2.16 on 2024-11-28 09:02

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('keywords', '0001_initial'),
        ('windows', '0001_initial'),
        ('executions', '0002_initial'),
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionCall',
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
            name='Sequence',
            fields=[
            ],
            options={
                'verbose_name': 'Sequenz',
                'verbose_name_plural': 'Sequenzen',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('windows.windowkeyword',),
        ),
        migrations.CreateModel(
            name='SequenceExecution',
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
            name='SequenceResourceImport',
            fields=[
            ],
            options={
                'verbose_name': 'Ressource-Import',
                'verbose_name_plural': 'Ressource-Imports',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('resources.resourceimport',),
        ),
        migrations.CreateModel(
            name='SequenceDocumentation',
            fields=[
            ],
            options={
                'verbose_name': 'Sequenz Dokumentation',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sequences.sequence',),
        ),
    ]
