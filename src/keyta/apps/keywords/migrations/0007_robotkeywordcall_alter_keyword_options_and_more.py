# Generated by Django 4.2.19 on 2025-02-24 10:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('keywords', '0006_extend_json_schema'),
    ]

    operations = [
        migrations.CreateModel(
            name='RobotKeywordCall',
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
        migrations.AlterModelOptions(
            name='keyword',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='keywordcallparameter',
            options={'ordering': ['parameter__type', 'parameter__position'], 'verbose_name': 'Parameter', 'verbose_name_plural': 'Parameters'},
        ),
    ]
