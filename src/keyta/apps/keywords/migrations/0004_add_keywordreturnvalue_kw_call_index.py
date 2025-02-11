from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('keywords', '0003_remove_keyword_everywhere'),
    ]

    operations = [
        migrations.AddField(
            model_name='keywordreturnvalue',
            name='kw_call_index',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        )
    ]
