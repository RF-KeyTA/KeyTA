from django.contrib import admin
from django.utils.translation import gettext as _

from adminsortable2.admin import SortableInlineAdminMixin

from .field_delete_related_instance import DeleteRelatedField


class BaseTabularInline(admin.TabularInline):
    extra = 0

    # by default readonly_fields is a tuple, which cannot be composed with a list
    def get_readonly_fields(self, request, obj=None):
        return list(super().get_readonly_fields(request, obj))

    @property
    def tab_name(self):
        return self.verbose_name_plural.lower()


class SortableTabularInline(SortableInlineAdminMixin, BaseTabularInline):
    template = 'sortable_tabular.html'


class SortableTabularInlineWithDelete(DeleteRelatedField, SortableTabularInline):
    pass


class TabularInlineWithDelete(DeleteRelatedField, BaseTabularInline):
    pass
