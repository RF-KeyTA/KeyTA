from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext as _

from adminsortable2.admin import SortableInlineAdminMixin

from keyta.widgets import related_field_widget_factory

from .field_delete_related_instance import DeleteRelatedField


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


class SortableTabularInline(SortableInlineAdminMixin, admin.TabularInline):
    template = 'sortable_tabular.html'
    
    # by default readonly_fields is a tuple, which cannot be composed with a list
    def get_readonly_fields(self, request, obj=None):
        return list(super().get_readonly_fields(request, obj))


class SortableTabularInlineWithDelete(DeleteRelatedField, SortableTabularInline):
    template = 'sortable_tabular.html'


class TabularInlineWithDelete(DeleteRelatedField, admin.TabularInline):
    pass
