from django.contrib import admin, messages
from django.http import HttpRequest

from apps.common.admin import BaseAdmin
from apps.common.forms import form_with_select
from apps.common.widgets import BaseSelect
from apps.windows.models import Window

from .models import System


class Windows(admin.TabularInline):
    model = Window.systems.through
    extra = 0
    max_num = 0
    can_delete = False
    show_change_link = True
    verbose_name = 'Maske'
    verbose_name_plural = 'Masken'

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(System)
class SystemAdmin(BaseAdmin):
    list_display = ['name', 'description']
    ordering = ['name']
    inlines = [Windows]
    fields = ['name', 'description', 'client', 'library']
    form = form_with_select(
        System,
        select_field='library',
        placeholder='Bibliothek auswählen'
    )

    def formfield_for_dbfield(self, db_field, request: HttpRequest, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if system_id := request.resolver_match.kwargs.get('object_id', None):
            if db_field.name == 'attach_to_system':
                field.widget = BaseSelect('Aktion auswählen')
                field.queryset = (
                    field.queryset.actions()
                    .filter(systems__in=[system_id])
                    .filter(setup_teardown=True)
                )

        return field

    def get_fields(self, request, obj=None):
        system: System = obj

        if system:
            return self.fields + ['attach_to_system']

        return self.fields

    def get_inlines(self, request, obj):
        system: System = obj

        if system and system.windows.first():
            return self.inlines

        return []

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        readonly_fields = []

        if request.user.is_superuser:
            return readonly_fields
        else:
            return readonly_fields + self.get_fields(request, obj)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            messages.warning(
                request,
                'Die Aktion zur Anbindung an das System muss gepflegt werden'
            )
