# Generated by Django 4.2.17 on 2025-01-28 08:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testcases', '0002_alter_testcase_options_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TestCaseExecution',
        ),
    ]
