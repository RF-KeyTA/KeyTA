import json
from django.db import migrations


def get_keyword_param_name(value, keyword_call):
    if value and keyword_call.from_keyword and value in keyword_call.from_keyword.parameters.values_list('name', flat=True):
        return value
    
    return ''


def extend_json_schema(apps, schema_editor):
    KeywordCallParameter = apps.get_model('keywords', 'KeywordCallParameter')

    for param in KeywordCallParameter.objects.all():
        keyword_call = param.keyword_call
        current_value = json.loads(param.value)
        value = current_value['value']

        new_value = {
            "pk": current_value['pk'],
            "user_input": current_value['value'],
            "arg_name": get_keyword_param_name(value, keyword_call),
            "kw_call_index": keyword_call.index
        }
        param.value = json.dumps(new_value)
        param.save()


class Migration(migrations.Migration):
    dependencies = [
        ('keywords', '0004_add_keywordreturnvalue_kw_call_index'),
    ]

    operations = [
        migrations.RunPython(extend_json_schema),
    ]
