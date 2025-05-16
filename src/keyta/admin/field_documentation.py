from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


class DocumentationField:
    def get_fields(self, request, obj=None):
        return ['readonly_documentation']

    def get_readonly_fields(self, request, obj=None):
        return ['readonly_documentation']

    @admin.display(description=_('Dokumentation'))
    def readonly_documentation(self, obj):
        return mark_safe(obj.documentation)
