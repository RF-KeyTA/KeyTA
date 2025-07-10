from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


class DocumentationField:
    def get_fields(self, request, obj=None):
        if not self.has_change_permission(request, obj):
            return self.fields + ['readonly_documentation']

        return self.fields + ['documentation']

    def get_readonly_fields(self, request, obj=None):
        if not self.has_change_permission(request, obj):
            return self.readonly_fields + ['readonly_documentation']

        return super().get_readonly_fields(request, obj)

    @admin.display(description=_('Dokumentation'))
    def readonly_documentation(self, obj):
        return mark_safe(obj.documentation)
