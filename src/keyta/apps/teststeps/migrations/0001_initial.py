# Generated by Django 4.2.17 on 2025-01-28 13:42

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('keywords', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestStep',
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
    ]
