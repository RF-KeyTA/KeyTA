from django.contrib import admin
from django.utils.safestring import mark_safe


class DocumentationField:
    fields = ['readonly_documentation']
    readonly_fields = ['readonly_documentation']

    @admin.display(description='')
    def readonly_documentation(self, obj):
        return mark_safe(obj.documentation)
