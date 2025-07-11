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
            return self.fields + [self.readonly_field]

        return self.fields + [self.field]
        
    def get_readonly_fields(self, request, obj=None):
        def readonly_field(obj):
            return mark_safe(getattr(obj, self.field))

        readonly_field.short_description = _(self.field.capitalize())

        if self.show_readonly(request, obj):
            setattr(self, self.readonly_field, readonly_field)

            return [
                readonly_field if readonly_field != self.field else self.readonly_field
                for readonly_field in self.readonly_fields
            ]

        return self.readonly_fields

    @property
    def readonly_field(self):
        return 'readonly_' + self.field

    def show_readonly(self, request, obj):
        return (
            self.field in self.readonly_fields or 
            not self.has_change_permission(request, obj)
        )


class DocumentationField(RichTextField):
    field = 'documentation'
