from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractUser

from adminsortable2.admin import SortableInlineAdminMixin

from .field_delete_related_instance import DeleteRelatedField


class BaseTabularInline(admin.TabularInline):
    extra = 0

    def can_change(self, user: AbstractUser, model: str):
        if app := settings.MODEL_TO_APP.get(model):
            return user.has_perm(f'{app}.change_{model}')

        return True

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
