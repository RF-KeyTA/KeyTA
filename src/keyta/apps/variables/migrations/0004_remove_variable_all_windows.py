# Generated by Django 4.2.17 on 2025-01-10 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('variables', '0003_windowvariable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variable',
            name='all_windows',
        ),
    ]
