from django.contrib import admin, messages
from django.db.models.functions import Lower
from django.http import HttpRequest
from django.utils.translation import gettext as _

from apps.common.admin import BaseAdmin, TabularInlineWithDelete
from apps.common.forms import form_with_select
from apps.windows.models import Window

from ..models.variable import Variable, VariableValue


class Values(TabularInlineWithDelete):
    model = VariableValue
    fields = ['name', 'value']
    extra = 0
    min_num = 1


class Windows(admin.TabularInline):
    model = Variable.windows.through
    extra = 0
    min_num = 1
    verbose_name = _('Maske')
    verbose_name_plural = _('Masken')

    form = form_with_select(
        Variable.windows.through,
        'window',
        _('Maske auswählen'),
        labels={
            'window': _('Maske')
        }
    )

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        variable: Variable = obj
        variable_systems = variable.systems.all()
        windows = Window.objects.filter(systems__in=variable_systems).distinct()
        formset.form.base_fields['window'].queryset = windows
        return formset


@admin.register(Variable)
class VariableAdmin(BaseAdmin):
    list_display = ['system_list', 'name', 'description']
    list_display_links = ['name']
    list_filter = ['systems']
    ordering = [Lower('name')]
    search_fields = ['name']
    search_help_text = _('Name')
    ordering = [Lower('name')]

    @admin.display(description=_('Systeme'))
    def system_list(self, obj):
        variable: Variable = obj

        if not variable.systems.exists():
            return _('System unabhängig')

        return list(variable.systems.values_list('name', flat=True))

    fields = ['name', 'description', 'setup_teardown']
    form = form_with_select(
        Variable,
        'systems',
        _('System hinzufügen'),
        select_many=True
    )
    inlines = [Values]

    def get_fields(self, request, obj=None):
        variable: Variable = obj

        if not variable or variable.all_windows:
            return ['all_windows', 'systems'] + self.fields

        if not variable.all_windows:
            return ['systems'] + self.fields

    def get_inlines(self, request, obj):
        variable: Variable = obj

        if not variable or variable.all_windows or not variable.systems.exists():
            return self.inlines

        return [Windows] + self.inlines

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        variable: Variable = obj

        if not variable:
            return []

        if variable.all_windows:
            readonly_fields = ['all_windows']
        else:
            readonly_fields = []

        if request.user.is_superuser:
            return readonly_fields
        else:
            return readonly_fields + super().get_readonly_fields(request, obj)

    def save_form(self, request, form, change):
        variable: Variable = super().save_form(request, form, change)

        if not change and not variable.all_windows:
            messages.warning(
                request,
                _('Der Referenzwert muss einer Maske zugeordnet werden')
            )

        return variable


@admin.register(VariableValue)
class VariableValueAdmin(BaseAdmin):
    pass
