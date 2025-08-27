from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest

from keyta.models.base_model import AbstractBaseModel
from keyta.widgets import link, Icon


class DeleteRelatedField:
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)

        if self.has_delete_permission(request, obj) and not 'delete' in fields:
            return fields + ['delete']

        return fields

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        @admin.display(description='')
        def delete(self, inline_obj: AbstractBaseModel):
            if not inline_obj.pk:
                return ''

            tab_url = inline_obj.get_tab_url(getattr(self, 'tab_name', None))

            return link(
                inline_obj.get_delete_url() + "?ref=" + request.path + tab_url,
                str(Icon(
                    settings.FA_ICONS.delete_rel,
                    {'font-size': '30px', 'margin-top': '3px'}
                ))
            )

        DeleteRelatedField.delete = delete
        readonly_fields = super().get_readonly_fields(request, obj)

        if self.has_delete_permission(request, obj):
            return readonly_fields + ['delete']

        return readonly_fields
