from django.contrib import admin
from django.http import HttpRequest

from adminsortable2.admin import SortableInlineAdminMixin

from apps.common.abc import AbstractBaseModel
from apps.common.widgets import link


class TabularInlineWithDelete(admin.TabularInline):
    @admin.display(description='')
    def delete(self, obj: AbstractBaseModel):
        if not obj.id:
            return ''

        return link(
            obj.get_delete_url() + "?ref=" + self.url + obj.get_tab_url(),
            '<i class="fa-solid fa-trash" '
            'style="font-size: 30px; margin-top: 3px"></i>'
        )

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        self.url = request.path

        if self.has_delete_permission(request, obj):
            return list(self.readonly_fields) + ['delete']

        return self.readonly_fields

    def get_fields(self, request, obj=None):
        if self.has_delete_permission(request, obj):
            return self.fields + ['delete']

        return self.fields

    def has_delete_permission(self, request: HttpRequest, obj=None):
        if obj:
            app, model = obj._meta.app_label, obj._meta.model_name
            return request.user.has_perm(f'{app}.delete_{model}', obj)

        return super().has_delete_permission(request, obj)


class SortableTabularInline(SortableInlineAdminMixin, admin.TabularInline):
    template = 'sortable_tabular.html'


class SortableTabularInlineWithDelete(
    SortableInlineAdminMixin,
    TabularInlineWithDelete
):
    template = 'sortable_tabular.html'
