from django import forms
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpRequest
from django.utils.translation import gettext_lazy as _

from model_clone import CloneModelAdminMixin

from keyta.admin.base_admin import BaseQuickAddAdmin
from keyta.apps.executions.admin import KeywordExecutionInline
from keyta.apps.keywords.admin import (
    ParametersInline,
    ReturnValueInline,
    WindowKeywordAdmin,
    WindowKeywordAdminMixin
)
from keyta.apps.keywords.models import KeywordCallReturnValue
from keyta.apps.libraries.models import Library, LibraryImport
from keyta.forms.baseform import form_with_select, BaseForm

from ..models import (
    Action,
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


class ActionForm(BaseForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        systems = self.cleaned_data.get('systems')
        action_systems = [
            system.name
            for system in self.initial.get('systems', [])
        ]

        if systems:
            if system := systems.values_list('name', flat=True).exclude(name__in=action_systems).filter(keywords__name=name).first():
                action = self._meta.model.objects.filter(name=name).filter(systems__name=system).filter(windows__isnull=True)
                if action.exists():
                    raise forms.ValidationError(
                        {
                            "name": _(f'Eine Aktion mit diesem Namen existiert bereits im System "{system}"')
                        }
                    )


@admin.register(Action)
class ActionAdmin(ActionAdminMixin, CloneModelAdminMixin, WindowKeywordAdmin):
    def get_list_filter(self, request):
        return super().get_list_filter(request) + ['setup_teardown']

    form = form_with_select(
        Action,
        'systems',
        _('System auswählen'),
        form_class=ActionForm,
        select_many=True
    )
    inlines = [
        Libraries,
        ParametersInline,
        ActionSteps
    ]

    def autocomplete_name_queryset(self, name: str, request: HttpRequest):
        return super().autocomplete_name_queryset(name, request).filter(windows__isnull=True)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if 'quick_change' in request.GET:
            action = ActionQuickChange.objects.get(pk=object_id)
            return HttpResponseRedirect(action.get_admin_url() + '?_popup=1' + '#' + request.GET['tab_name'])

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

        kw_call_pks = action.calls.values_list('pk')
        if KeywordCallReturnValue.objects.filter(keyword_call__in=kw_call_pks).exists():
            inlines += [ReturnValueInline]

        if not action.has_empty_sequence:
            return inlines + [KeywordExecutionInline]

        return inlines

    def get_protected_objects(self, obj):
        action: Action = obj
        return action.uses.filter(execution__isnull=True)


class QuickAddActionForm(BaseForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        windows = self.cleaned_data.get('windows')

        if len(windows) == 1:
            window = windows[0]
            if window.actions.filter(name=name).exists():
                raise forms.ValidationError(
                    {
                        "name": _(f'Eine Aktion mit diesem Namen existiert bereits in der Maske "{window.name}"')
                    }
                )


@admin.register(ActionQuickAdd)
class ActionQuickAddAdmin(ActionAdminMixin, BaseQuickAddAdmin):
    form = QuickAddActionForm

    def autocomplete_name_queryset(self, name: str, request: HttpRequest):
        queryset = super().autocomplete_name_queryset(name, request)

        if 'windows' in request.GET:
            queryset = queryset.filter(windows__in=[request.GET['windows']])

        return queryset


@admin.register(ActionQuickChange)
class ActionQuickChangeAdmin(WindowKeywordAdmin):
    fields = []
    readonly_fields = ['documentation']
    inlines = [ParametersInline, ActionSteps]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return super().change_view(request, object_id, form_url, extra_context or {'title_icon': settings.FA_ICONS.action})

    def get_inlines(self, request, obj):
        action: Action = obj
        inlines = [*self.inlines]

        kw_call_pks = action.calls.values_list('pk')
        if KeywordCallReturnValue.objects.filter(keyword_call__in=kw_call_pks).exists():
            inlines += [ReturnValueInline]

        return inlines

    def has_delete_permission(self, request, obj=None):
        return False
