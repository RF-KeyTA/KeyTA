from django.conf import settings
from django.contrib import admin
from django.forms import ModelMultipleChoiceField
from django.http import HttpResponseRedirect, HttpRequest
from django.urls import reverse
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
from keyta.apps.keywords.models.keywordcall import KeywordCallType
from keyta.apps.libraries.models import Library, LibraryImport
from keyta.apps.systems.models import System
from keyta.forms import form_with_select
from keyta.widgets import CheckboxSelectMultipleSystems, url_query_parameters

from ..forms import ActionForm, QuickAddActionForm
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
        ActionSteps,
        ReturnValueInline
    ]

    def autocomplete_name_queryset(self, name: str, request: HttpRequest):
        return super().autocomplete_name_queryset(name, request).filter(windows__isnull=True)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        steps_tab = '#%s-tab' % _('Schritte').lower()

        if 'steps_tab' in request.GET:
            return HttpResponseRedirect(request.path_info + steps_tab)

        if '_popup' in request.GET:
            action = ActionQuickChange.objects.get(pk=object_id)
            return HttpResponseRedirect(action.get_admin_url() + '?' + url_query_parameters(request.GET) + steps_tab)

        current_app, model, *route = request.resolver_match.route.split('/')
        app = settings.MODEL_TO_APP.get(model)

        if app and app != current_app:
            return HttpResponseRedirect(reverse('admin:%s_%s_change' % (app, model), args=(object_id,)))

        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'systems':
            field = ModelMultipleChoiceField(
                widget=CheckboxSelectMultipleSystems,
                queryset=field.queryset
            )
            field.label = _('Systeme')

            if action_id := request.resolver_match.kwargs.get('object_id'):
                action = Action.objects.get(id=action_id)
                attach_to_systems = System.objects.filter(attach_to_system=action).values_list('pk', flat=True)

                if attach_to_systems.exists():
                    field.widget.in_use = set(attach_to_systems)

        return field

    def get_fields(self, request, obj=None):
        action: Action = obj
        fields =  super().get_fields(request, action)

        return ['setup_teardown', 'systems'] + fields

    def get_inlines(self, request, obj):
        action: Action = obj
        inlines = [Windows] + self.inlines

        if not action:
            return [ParametersInline]

        if not action.has_empty_sequence:
            return inlines + [KeywordExecutionInline]

        return inlines

    def get_protected_objects(self, obj):
        action: Action = obj
        return action.uses.exclude(type=KeywordCallType.KEYWORD_EXECUTION)

    def has_add_permission(self, request):
        return self.can_add(request.user, 'action')

    def has_change_permission(self, request, obj=None):
        action: Action = obj

        if action and action.setup_teardown:
            return request.user.is_superuser

        return self.can_change(request.user, 'action')

    def has_delete_permission(self, request, obj=None):
        action: Action = obj

        if action and action.setup_teardown:
            return request.user.is_superuser

        return self.can_delete(request.user, 'action')


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

    def has_change_permission(self, request, obj=None):
        return self.can_change(request.user, 'action')

    def has_delete_permission(self, request, obj=None):
        return False
