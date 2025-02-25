from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest

from keyta.models.base_model import AbstractBaseModel
from keyta.widgets import link, Icon


class DeleteRelatedField:
    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj) + ['delete']

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        @admin.display(description='')
        def delete(self, obj: AbstractBaseModel):
            if not obj.id:
                return ''

            tab_url = obj.get_tab_url(getattr(self, 'tab_name', None))

            return link(
                obj.get_delete_url() + "?ref=" + request.path + tab_url,
                str(Icon(
                    settings.FA_ICONS.delete_rel,
                    {'font-size': '30px', 'margin-top': '3px'}
                ))
            )

        DeleteRelatedField.delete = delete
        return super().get_readonly_fields(request, obj) + ['delete']
