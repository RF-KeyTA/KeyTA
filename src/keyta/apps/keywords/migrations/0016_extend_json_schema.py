import json

from django.db import migrations

from keyta.apps.keywords.keywordcall_parameter_json_value import JSONValue

from ..models.keywordcall_parameters import KeywordCallParameter


def extend_json_schema(apps, schema_editor):
    for param in KeywordCallParameter.objects.all():
        current_value = json.loads(param.value)
        value = current_value['value']
        pk = current_value['pk']

        if pk:
            param.update_value()
        else:
            param.value = JSONValue(
                arg_name=None,
                kw_call_index=None,
                pk=None,
                user_input=value
            ).jsonify()
            param.save()


class Migration(migrations.Migration):
    dependencies = [
        ('keywords', '0015_alter_keywordcall_condition'),
    ]

    operations = [
        migrations.RunPython(extend_json_schema),
    ]
