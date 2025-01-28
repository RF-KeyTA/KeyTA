from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseAdmin, BaseAddAdmin
from keyta.admin.base_inline import TabularInlineWithDelete
from keyta.forms.baseform import form_with_select

from apps.executions.admin import KeywordExecutionInline
from apps.keywords.admin import KeywordDocumentationAdmin
from apps.libraries.models import Library
from apps.windows.admin import (
    WindowKeywordParameters,
    WindowKeywordAdmin,
    WindowKeywordAdminMixin,
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


class ActionAdminMixin(WindowKeywordAdminMixin):
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


class Execution(KeywordExecutionInline):
    model = ActionExecution


class Windows(TabularInlineWithDelete):
    model = ActionWindow
    fields = ['window']
    extra = 0
    tab_name = _('Masken').lower()
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

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
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
    tab_name = _('Bibliotheken').lower()
    verbose_name = _('Bibliothek')
    verbose_name_plural = _('Bibliotheken')

    def get_max_num(self, request, obj=None, **kwargs):
        return Library.objects.count()

    def get_field_queryset(self, db, db_field, request: HttpRequest):
        action_id = request.resolver_match.kwargs['object_id']
        field_queryset = super().get_field_queryset(db, db_field, request)
        imported_libraries = (
            self.get_queryset(request)
            .filter(keyword_id__in=[action_id])
            .values_list('library_id', flat=True)
        )

        return field_queryset.exclude(id__in=imported_libraries)

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


@admin.register(Action)
class ActionAdmin(ActionAdminMixin, WindowKeywordAdmin):
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

        return ['setup_teardown', 'systems'] + fields

    def get_inlines(self, request, obj):
        action: Action = obj

        if not action:
            return [WindowKeywordParameters]

        inlines = [Windows] + self.inlines

        if not action.has_empty_sequence:
            return inlines + [WindowKeywordReturnValues, Execution]

        return inlines

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        action: Action = obj

        if not action:
            return []

        readonly_fields = []

        if request.user.is_superuser:
            return readonly_fields
        else:
            return readonly_fields + super().get_readonly_fields(request, obj)


@admin.register(ActionDocumentation)
class ActionDocumentationAdmin(KeywordDocumentationAdmin):
    pass


@admin.register(ActionWindow)
class ActionWindowAdmin(BaseAdmin):
    pass


@admin.register(WindowAction)
class WindowActionAdmin(ActionAdminMixin, BaseAddAdmin):
    pass
