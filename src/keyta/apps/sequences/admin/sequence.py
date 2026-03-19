from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.options import csrf_protect_m
from django.db import transaction, router
from django.forms import ModelMultipleChoiceField
from django.http import HttpResponseRedirect, HttpRequest
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
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
from .uses_inline import UsesInline


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

    def get_list_display(self, request):
        return ['empty'] + super().get_list_display(request)

    @admin.display(description='')
    def empty(self, obj):
        return mark_safe('&nbsp;')

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
    unlock_confirmation_template = 'unlock_confirmation.html'

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        sequence = Sequence.objects.get(id=object_id)
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

        context = {
            'title_icon': settings.FA_ICONS.sequence
        }

        if 'lock' in request.GET:
            sequence.lock()
            return HttpResponseRedirect(request.path)

        if 'unlock' in request.GET:
            sequence.unlock()

            if request.method == 'POST':
                return HttpResponseRedirect(request.path)

            return self.unlock_view(request, object_id, extra_context)

        if sequence.in_use <= 1:
            sequence.unlock()

        if sequence.in_use > 1 and sequence.unlock_timeout_expired:
            sequence.lock()

        if sequence.locked:
            context.update({
                'change_lock': {
                    'next_state': 'unlock',
                    'icon': 'unlock'
                }
            })
            messages.warning(request, _('Die Sequenz ist zur Bearbeitung gesperrt. Zum Entsperren das offene Schloss anklicken.'))
        else:
            context.update({
                'change_lock': {
                    'next_state': 'lock',
                    'icon': 'lock'
                }
            })

        return super().change_view(request, object_id, form_url=form_url, extra_context=context | (extra_context or {}))

    @csrf_protect_m
    def unlock_view(self, request, object_id, extra_context=None):
        if request.method in ("GET", "HEAD", "OPTIONS", "TRACE"):
            return self._unlock_view(request, object_id, extra_context)

        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._unlock_view(request, object_id, extra_context)

    def _unlock_view(self, request, object_id, extra_context):
        "The 'unlock' admin view for this model."
        app_label = self.opts.app_label

        sequence = Sequence.objects.get(id=object_id)

        if sequence is None:
            return self._get_obj_does_not_exist_redirect(request, self.opts, object_id)

        # Populate deleted_objects, a data structure of all related objects that
        # will also be deleted.
        (
            deleted_objects,
            model_count,
            perms_needed,
            protected,
        ) = self.get_deleted_objects([sequence], request)

        if request.POST and not protected:  # The user has confirmed the deletion.
            sequence.unlock()
            return HttpResponseRedirect(request.path)

        object_name = str(self.opts.verbose_name)

        context = {
            **self.admin_site.each_context(request),
            "subtitle": None,
            "object_name": object_name,
            "object": sequence,
            "deleted_objects": deleted_objects,
            "model_count": dict(model_count).items(),
            "perms_lacking": perms_needed,
            "protected": protected,
            "opts": self.opts,
            "app_label": app_label,
            "preserved_filters": self.get_preserved_filters(request),
            **(extra_context or {}),
        }

        return self.render_unlock_form(request, context)

    def render_unlock_form(self, request, context):
        request.current_app = self.admin_site.name
        context.update(
            media=self.media,
        )

        return TemplateResponse(
            request,
            self.unlock_confirmation_template,
            context,
        )

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
            inlines += [KeywordExecutionInline]

        if sequence.in_use > 0:
            inlines +=  [UsesInline]

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
        locked = False

        if '/sequence/' in request.path and '/change/' in request.path:
            if sequence_id := request.resolver_match.kwargs.get('object_id'):
                sequence = Sequence.objects.get(id=sequence_id)
                locked = sequence.locked

        return self.can_change(request.user, 'sequence') and not locked

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
            if field != 'exec_state'
        ]


@admin.register(SequenceQuickChange)
class SequenceQuickChangeAdmin(WindowKeywordAdmin):
    fields = []
    readonly_fields = ['documentation']
    inlines = [ParametersInline, SequenceQuickChangeSteps]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        sequence = Sequence.objects.get(id=object_id)

        if sequence.in_use > 1 and sequence.unlock_timeout_expired:
            sequence.lock()

        return super().change_view(request, object_id, form_url, extra_context or {'title_icon': settings.FA_ICONS.sequence})

    def get_inlines(self, request, obj):
        sequence: Sequence = obj
        inlines = [*self.inlines]

        kw_call_pks = sequence.calls.values_list('pk')
        if KeywordCallReturnValue.objects.filter(keyword_call__in=kw_call_pks).exists():
            inlines += [ReturnValueInline]

        return inlines

    def has_change_permission(self, request, obj=None):
        locked = False

        if '/sequencequickchange/' in request.path:
            sequence_id = request.resolver_match.kwargs.get('object_id')
            sequence = Sequence.objects.get(id=sequence_id)
            locked = sequence.locked

        return self.can_change(request.user, 'sequence') and not locked

    def has_delete_permission(self, request, obj=None):
        return False
