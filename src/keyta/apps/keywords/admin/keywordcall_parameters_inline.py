from django.contrib import admin

from apps.keywords.forms import KeywordCallParameterFormset
from apps.keywords.models import KeywordCallParameter


class KeywordCallParametersInline(admin.TabularInline):
    model = KeywordCallParameter
    fields = ['name', 'value']
    readonly_fields = ['name']
    extra = 0
    formset = KeywordCallParameterFormset
    max_num = 0
    can_delete = False

    def name(self, obj: KeywordCallParameter):
        return obj.name.replace('_', ' ')
