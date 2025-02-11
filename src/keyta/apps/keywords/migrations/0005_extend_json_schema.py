import json

from django.db import migrations

from keyta.select_value import SelectValue

from ..models.keywordcall_parameter_source import KeywordCallParameterSource


def extend_json_schema(apps, schema_editor):
    KeywordCallParameter = apps.get_model('keywords', 'KeywordCallParameter')

    for param in KeywordCallParameter.objects.all():
        current_value = json.loads(param.value)
        value = current_value['value']
        pk = current_value['pk']

        if pk:
            param_source = KeywordCallParameterSource.objects.get(id=pk)
            new_value = param_source.jsonify()
        else:
            new_value = SelectValue(
                arg_name=None,
                kw_call_index=None,
                pk=None,
                user_input=value
            ).jsonify()

        param.value = new_value
        param.save()


class Migration(migrations.Migration):
    dependencies = [
        ('keywords', '0004_add_keywordreturnvalue_kw_call_index'),
    ]

    operations = [
        migrations.RunPython(extend_json_schema),
    ]
