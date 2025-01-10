from django.contrib import admin, messages
from django.http import HttpRequest
from django.utils.translation import gettext as _

from apps.common.admin import BaseAddAdmin, TabularInlineWithDelete
from apps.common.forms.baseform import form_with_select
from apps.executions.admin import KeywordExecutionInline
from apps.keywords.admin import KeywordDocumentationAdmin
from apps.libraries.models import Library
from apps.windows.admin import (
    WindowKeywordParameters,
    WindowKeywordAdmin,
    WindowKeywordReturnValues
)
from apps.windows.models import Window

from ..models import (
    Action,
    ActionDocumentation,
    ActionExecution,
    ActionLibraryImport,
    ActionWindow,
    WindowAction
)
from .steps_inline import ActionSteps


class Execution(KeywordExecutionInline):
    model = ActionExecution


@admin.register(ActionWindow)
class ActionWindowAdmin(admin.ModelAdmin):
    pass


@admin.register(WindowAction)
class WindowActionAdmin(BaseAddAdmin):
    pass


class Windows(TabularInlineWithDelete):
    model = ActionWindow
    fields = ['window']
    extra = 0
    min_num = 1
    verbose_name = _('Maske')
    verbose_name_plural = _('Masken')

    form = form_with_select(
        ActionWindow,
        'window',
        _('Maske auswählen'),
        labels={
            'window': _('Maske')
        }
    )

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        action: Action = obj
        action_systems = action.systems.all()
        windows = Window.objects.filter(systems__in=action_systems).distinct()
        formset.form.base_fields['window'].label = 'Maske'
        formset.form.base_fields['window'].queryset = windows
        return formset

    def has_change_permission(self, request: HttpRequest, obj) -> bool:
        return False


class Libraries(TabularInlineWithDelete):
    fk_name = 'keyword'
    model = ActionLibraryImport
    fields = ['library']
    extra = 0
    form = form_with_select(
        ActionLibraryImport,
        'library',
        _('Bibliothek auswählen')
    )
    verbose_name = _('Bibliothek')
    verbose_name_plural = _('Bibliotheken')

    def has_change_permission(self, request: HttpRequest, obj) -> bool:
        return False


@admin.register(Action)
class ActionAdmin(WindowKeywordAdmin):
    form = form_with_select(
        Action,
        'systems',
        _('System auswählen'),
        select_many=True
    )
    inlines = [
        Libraries,
        WindowKeywordParameters,
        ActionSteps
    ]

    def get_fields(self, request, obj=None):
        action: Action = obj

        fields =  super().get_fields(request, obj)

        if not action or action.everywhere:
            return ['everywhere', 'systems'] + fields + ['setup_teardown']

        if not action.everywhere:
            return ['systems'] + fields + ['setup_teardown']

    def get_inlines(self, request, obj):
        action: Action = obj

        if not action:
            return [WindowKeywordParameters]

        inlines = self.inlines

        if not action.everywhere:
            inlines = [Windows] + self.inlines

        if not action.has_empty_sequence:
            return inlines + [WindowKeywordReturnValues, Execution]

        return inlines

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        action: Action = obj

        if not action:
            return []

        if action.everywhere:
            readonly_fields = ['everywhere']
        else:
            readonly_fields = []

        if request.user.is_superuser:
            return readonly_fields
        else:
            return readonly_fields + super().get_readonly_fields(request, obj)

    def save_form(self, request, form, change):
        action: Action = super().save_form(request, form, change)

        if not change and not action.everywhere:
            messages.warning(
                request,
                _('Die Aktion muss einer Maske zugeordnet werden')
            )

        return action

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            form.save_m2m()

            action: Action = obj
            library_ids = set(action.systems.values_list('library', flat=True))
            for library_id in library_ids:
                ActionLibraryImport.objects.create(
                    keyword=action,
                    library=Library.objects.get(id=library_id),
                )


@admin.register(ActionDocumentation)
class ActionDocumentationAdmin(KeywordDocumentationAdmin):
    pass
