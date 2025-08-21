from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from tinymce.widgets import AdminTinyMCE


class RichTextField:
    formfield_overrides = {
        models.TextField: {
            'widget': AdminTinyMCE
        }
    }

    def get_fields(self, request, obj=None):
        if self.show_readonly(request, obj):
            return self.fields + ['readonly_documentation']

        return self.fields + [self.field]

    @admin.display(description=_('Dokumentation'))
    def readonly_documentation(self, obj):
        return mark_safe(getattr(obj, self.field))

    def get_readonly_fields(self, request, obj=None):
        if self.show_readonly(request, obj):
            return [
                readonly_field if readonly_field != self.field else 'readonly_documentation'
                for readonly_field in self.readonly_fields
            ]

        return self.readonly_fields

    def show_readonly(self, request, obj):
        return (
            self.field in self.readonly_fields or
            not self.has_change_permission(request, obj)
        )


class DocumentationField(RichTextField):
    field = 'documentation'
