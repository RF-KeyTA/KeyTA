from django.contrib import admin

from ..forms import KeywordCallParameterFormset
from ..models import KeywordCallParameter


class KeywordCallParametersInline(admin.TabularInline):
    model = KeywordCallParameter
    fields = ['name', 'value']
    readonly_fields = ['name']
    formset = KeywordCallParameterFormset
    extra = 0
    max_num = 0
    can_delete = False

    def name(self, obj: KeywordCallParameter):
        return obj.name.replace('_', ' ').title()

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('parameter__position')
