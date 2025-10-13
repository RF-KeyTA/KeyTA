from django import forms
from django.conf import settings
from django.contrib import admin
from django.forms import ModelMultipleChoiceField
from django.http import HttpResponseRedirect, HttpRequest
from django.urls import reverse
from django.utils.translation import gettext as _

from model_clone import CloneModelAdminMixin

from keyta.admin.base_admin import BaseQuickAddAdmin
from keyta.admin.list_filters import SystemListFilter
from keyta.apps.executions.admin import KeywordExecutionInline
from keyta.apps.keywords.admin import (
    ParametersInline,
    ReturnValueInline,
    WindowKeywordAdmin,
    WindowKeywordAdminMixin,
)
from keyta.apps.keywords.models import KeywordCallReturnValue
from keyta.apps.windows.models import Window
from keyta.widgets import (
    CheckboxSelectMultipleSystems,
    Icon,
    ManyToManySelectOneWidget,
    link,
    url_query_parameters
)

from ..forms import QuickAddSequenceForm, SequenceForm
from ..models import (
    Sequence,
    SequenceQuickAdd,
    SequenceQuickChange
)
from .steps_inline import SequenceSteps


class WindowListFilter(admin.RelatedFieldListFilter):
    @property
    def include_empty_choice(self):
        return False


@admin.register(Sequence)
class SequenceAdmin(CloneModelAdminMixin, WindowKeywordAdmin):
    list_filter = [
        ('systems', SystemListFilter),
        ('windows', WindowListFilter)
    ]

    form = forms.modelform_factory(
        Sequence,
        SequenceForm,
        fields=[],
        labels={
            'systems': _('Systeme')
        },
        widgets={
            'systems': ManyToManySelectOneWidget(
                placeholder=_('System auswählen'),
                model=Sequence.systems.through,
                search_fields=['name__icontains'],
            ),
            'windows': ManyToManySelectOneWidget(
                placeholder=_('Maske auswählen'),
                model=Sequence.windows.through,
                search_fields=['name__icontains'],
                dependent_fields={'systems': 'systems'},
            )
        }
    )
    inlines = [
        ParametersInline,
        SequenceSteps
    ]

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        steps_tab = '#%s-tab' % _('Schritte').lower()

        if 'steps_tab' in request.GET:
            return HttpResponseRedirect(request.path_info + steps_tab)

        if '_popup' in request.GET:
            sequence = SequenceQuickChange.objects.get(pk=object_id)
            return HttpResponseRedirect(sequence.get_admin_url() + '?' + url_query_parameters(request.GET) + steps_tab)

        current_app, model, *route = request.resolver_match.route.split('/')
        app = settings.MODEL_TO_APP.get(model)

        if app and app != current_app:
            return HttpResponseRedirect(reverse('admin:%s_%s_change' % (app, model), args=(object_id,)))

        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'systems' and '/change/' in request.path:
            field = ModelMultipleChoiceField(
                widget=CheckboxSelectMultipleSystems,
                queryset=field.queryset
            )
            field.label = _('Systeme')

            if sequence_id := request.resolver_match.kwargs.get('object_id'):
                sequence = Sequence.objects.get(id=sequence_id)
                window_systems = sequence.windows.values_list('systems', flat=True)
                field.queryset = field.queryset.filter(pk__in=window_systems)

        return field

    def get_fields(self, request, obj=None):
        sequence: Sequence = obj

        fields = ['systems'] 

        if sequence and (sequence.calls.exists() or sequence.uses.filter(testcase__isnull=False).exists()):
            return fields + ['window'] + super().get_fields(request, obj)

        return fields + ['windows'] + super().get_fields(request, obj)

    def get_inlines(self, request, obj):
        sequence: Sequence = obj
        inlines = [*self.inlines]

        if not sequence:
            return [ParametersInline]

        kw_call_pks = sequence.calls.values_list('pk')
        if KeywordCallReturnValue.objects.filter(keyword_call__in=kw_call_pks).exists():
            inlines += [ReturnValueInline]

        if not sequence.has_empty_sequence:
            return inlines + [KeywordExecutionInline]

        return inlines

    def get_protected_objects(self, obj):
        sequence: Sequence = obj
        return sequence.uses.filter(execution__isnull=True)

    def get_readonly_fields(self, request, obj):
        sequence: Sequence = obj

        if sequence and (sequence.calls.exists() or sequence.uses.filter(testcase__isnull=False).exists()):
            return ['window']
        
        return super().get_readonly_fields(request, obj)

    def has_add_permission(self, request):
        return self.can_add(request.user, 'sequence')

    def has_change_permission(self, request, obj=None):
        return self.can_change(request.user, 'sequence')

    def has_delete_permission(self, request, obj=None):
        return self.can_delete(request.user, 'sequence')

    @admin.display(description=_('Maske'))
    def window(self, sequence: Sequence):
        window: Window = sequence.windows.first()
        icon = Icon(settings.FA_ICONS.go_to, styles={'font-size': '0.7rem', 'margin-left': '2px'})

        return link(
            window.get_admin_url(),
            f'{window.name} {icon}',
            new_page=True
        )


@admin.register(SequenceQuickAdd)
class SequenceQuickAddAdmin(WindowKeywordAdminMixin, BaseQuickAddAdmin):
    form = QuickAddSequenceForm


class SequenceQuickChangeSteps(SequenceSteps):
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)

        return [
            field
            for field in fields
            if field != 'execute'
        ]


@admin.register(SequenceQuickChange)
class SequenceQuickChangeAdmin(WindowKeywordAdmin):
    fields = []
    readonly_fields = ['documentation']
    inlines = [ParametersInline, SequenceQuickChangeSteps]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return super().change_view(request, object_id, form_url, extra_context or {'title_icon': settings.FA_ICONS.sequence})

    def get_inlines(self, request, obj):
        sequence: Sequence = obj
        inlines = [*self.inlines]

        kw_call_pks = sequence.calls.values_list('pk')
        if KeywordCallReturnValue.objects.filter(keyword_call__in=kw_call_pks).exists():
            inlines += [ReturnValueInline]

        return inlines

    def has_change_permission(self, request, obj=None):
        return self.can_change(request.user, 'sequence')

    def has_delete_permission(self, request, obj=None):
        return False
