import json

from django.contrib import admin
from django.db.models.functions import Lower
from django.http import HttpRequest
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseAdmin, BaseAddAdmin
from keyta.admin.base_inline import TabularInlineWithDelete
from keyta.forms import form_with_select

from apps.windows.models import Window

from ..models import Variable, VariableValue, VariableWindow, WindowVariable


class Values(TabularInlineWithDelete):
    model = VariableValue
    fields = ['name', 'value']
    extra = 1
    min_num = 1


class Windows(TabularInlineWithDelete):
    model = VariableWindow
    extra = 0
    fields = ['window']
    tab_name = _('Masken').lower()
    verbose_name = _('Maske')
    verbose_name_plural = _('Masken')

    form = form_with_select(
        VariableWindow,
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

    def has_change_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Variable)
class VariableAdmin(BaseAdmin):
    list_display = ['system_list', 'name', 'description']
    list_display_links = ['name']
    list_filter = ['systems']
    ordering = [Lower('name')]
    search_fields = ['name']
    search_help_text = _('Name')

    @admin.display(description=_('Systeme'))
    def system_list(self, obj):
        variable: Variable = obj

        if not variable.systems.exists():
            return _('System unabhängig')

        return list(variable.systems.values_list('name', flat=True))

    fields = ['systems', 'name', 'description']
    form = form_with_select(
        Variable,
        'systems',
        _('System hinzufügen'),
        select_many=True
    )
    inlines = [Values]

    def autocomplete_name(self, name: str):
        return json.dumps([
            '%s (%s :: %s)' % (name, systems, windows or _('Systemweit'))
            for name, systems, windows in
            self.model.objects.values_list('name', 'systems__name', 'windows__name')
            .filter(name__icontains=name)
        ])

    def get_inlines(self, request, obj):
        variable: Variable = obj

        if not variable or not variable.systems.exists():
            return self.inlines

        return [Windows] + self.inlines

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        variable: Variable = obj

        if not variable:
            return []

        readonly_fields = []

        if request.user.is_superuser:
            return readonly_fields
        else:
            return readonly_fields + super().get_readonly_fields(request, obj)


@admin.register(VariableValue)
class VariableValueAdmin(BaseAdmin):
    pass


@admin.register(VariableWindow)
class VariableWindowAdmin(BaseAdmin):
    pass


@admin.register(WindowVariable)
class WindowVariableAdmin(BaseAddAdmin):
    inlines = [Values]
