# Generated by Django 4.2.17 on 2025-01-28 13:42

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('resources', '0001_initial'),
        ('executions', '0002_initial'),
        ('windows', '0001_initial'),
        ('keywords', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionCall',
            fields=[
            ],
            options={
                'verbose_name': 'Step',
                'verbose_name_plural': 'Steps',
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
                'verbose_name': 'Sequence',
                'verbose_name_plural': 'Sequences',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('keywords.windowkeyword',),
        ),
        migrations.CreateModel(
            name='SequenceExecution',
            fields=[
            ],
            options={
                'verbose_name': 'Execution',
                'verbose_name_plural': 'Execution',
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
                'verbose_name': 'Resource Import',
                'verbose_name_plural': 'Resource Imports',
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
                'verbose_name': 'Sequence Documentation',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sequences.sequence',),
        ),
        migrations.CreateModel(
            name='WindowSequence',
            fields=[
            ],
            options={
                'verbose_name': 'Sequence',
                'verbose_name_plural': 'Sequences',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sequences.sequence',),
        ),
    ]
