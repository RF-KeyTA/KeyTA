import json

from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from model_clone import CloneModelAdminMixin

from keyta.admin.base_admin import BaseAdmin, BaseQuickAddAdmin
from keyta.apps.executions.admin import KeywordExecutionInline
from keyta.apps.keywords.admin import (
    ParametersInline,
    ReturnValueInline,
    WindowKeywordAdmin,
    WindowKeywordAdminMixin
)
from keyta.apps.libraries.models import Library, LibraryImport
from keyta.forms.baseform import form_with_select

from ..models import (
    Action,
    ActionWindowRelation,
    ActionQuickAdd,
    ActionQuickChange
)
from .libraries_inline import Libraries
from .steps_inline import ActionSteps
from .windows_inline import Windows


class ActionAdminMixin(WindowKeywordAdminMixin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            form.save_m2m()

            action: Action = obj
            library_ids = action.systems.values_list('library', flat=True).distinct()
            
            for library in Library.objects.filter(id__in=library_ids):
                LibraryImport.objects.create(
                    keyword=action,
                    library=library,
                )


@admin.register(Action)
class ActionAdmin(ActionAdminMixin, CloneModelAdminMixin, WindowKeywordAdmin):
    def get_list_filter(self, request):
        return super().get_list_filter(request) + ['setup_teardown']

    form = form_with_select(
        Action,
        'systems',
        _('System auswählen'),
        select_many=True
    )
    inlines = [
        Libraries,
        ParametersInline,
        ActionSteps
    ]

    def autocomplete_name(self, name: str, request: HttpRequest):
        names = list(
            self.model.objects
            .filter(name__icontains=name)
            .filter(windows__isnull=True)
            .values_list('name', flat=True)
        )

        return json.dumps(names)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if 'quick_change' in request.GET:
            action = ActionQuickChange.objects.get(pk=object_id)
            return HttpResponseRedirect(action.get_admin_url())

        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def get_fields(self, request, obj=None):
        action: Action = obj
        fields =  super().get_fields(request, action)

        return ['setup_teardown', 'systems'] + fields

    def get_inlines(self, request, obj):
        action: Action = obj
        inlines = [Windows] + self.inlines

        if not action:
            return [ParametersInline]

        if action.calls.filter(return_values__isnull=False).exists():
            inlines += [ReturnValueInline]

        if not action.has_empty_sequence:
            return inlines + [KeywordExecutionInline]

        return inlines


@admin.register(ActionQuickAdd)
class ActionQuickAddAdmin(ActionAdminMixin, BaseQuickAddAdmin):
    pass


@admin.register(ActionQuickChange)
class ActionQuickChangeAdmin(WindowKeywordAdmin):
    inlines = [ParametersInline, ActionSteps, ReturnValueInline]

    def has_delete_permission(self, request, obj=None):
        return False

    def get_fields(self, request, obj=None):
        return self.get_readonly_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        return ['readonly_documentation']


@admin.register(ActionWindowRelation)
class ActionWindowRelationAdmin(BaseAdmin):
    pass
