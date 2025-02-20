# Generated by Django 4.2.16 on 2024-11-28 09:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('keywords', '0001_initial'),
        ('libraries', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='System',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Name')),
                ('description', models.CharField(max_length=255, verbose_name='Beschreibung')),
                ('client', models.CharField(blank=True, max_length=255, null=True, verbose_name='Mandant')),
                ('attach_to_system', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='keywords.keyword', verbose_name='Anbindung an laufendes System')),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='libraries.library', verbose_name='Automatisierung')),
            ],
            options={
                'verbose_name': 'System',
                'verbose_name_plural': 'Systeme',
            },
        ),
    ]
