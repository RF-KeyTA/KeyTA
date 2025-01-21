from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext as _

from adminsortable2.admin import SortableInlineAdminMixin

from apps.common.abc import AbstractBaseModel
from apps.common.widgets import link, related_field_widget_factory


class TabularInlineWithDelete(admin.TabularInline):
    @admin.display(description='')
    def delete(self, obj: AbstractBaseModel):
        if not obj.id:
            return ''

        return link(
            obj.get_delete_url() + "?ref=" + self.url + obj.get_tab_url(getattr(self, 'tab_name', None)),
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

    # 1. TabularInlineWithDelete appends the Delete field
    # 2. admin/js/inlines.js inserts the Remove button in the last cell of a row
    # 3. SortableInlineAdminMixin appends the hidden default_order_field
    # This is incompatible with 1. and 2. Therefore, we prepend the default_order_field
    def get_fields(self, *args, **kwargs):
        *fields, default_order_field = list(super().get_fields(*args, **kwargs))
        return [self.default_order_field] + fields


class AddInline(admin.TabularInline):
    def formfield_for_dbfield(self, db_field, request: HttpRequest, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == self.related_field_name:
            field.widget = related_field_widget_factory(
                self.related_field_widget_url(self.related_field_model),
                self.related_field_widget_url_params(request),
                field.widget
            )
            field.widget.can_change_related = False
            field.widget.can_view_related = False
            field.widget.attrs.update({
                'data-placeholder': _('Klicke auf das Plus-Symbol'),
                'disabled': True
            })

        return field

    def related_field_widget_url(self, model_class):
        app = model_class._meta.app_label
        model = model_class._meta.model_name

        return reverse('admin:%s_%s_add' % (app, model))

    def related_field_widget_url_params(self, request: HttpRequest):
        return {}
