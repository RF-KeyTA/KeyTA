from django import forms
from django.conf import settings
from django.contrib import admin
from django.forms import ModelMultipleChoiceField
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

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
from keyta.apps.systems.models import System
from keyta.apps.windows.models import Window
from keyta.forms.baseform import BaseForm
from keyta.widgets import (
    CheckboxSelectMultipleSystems,
    ModelSelect2MultipleAdminWidget,
    Select2MultipleWidget,
    link
)

from ..forms import SequenceStepsFormset
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


class SequenceForm(BaseForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        systems = self.cleaned_data.get('systems')
        windows = self.cleaned_data.get('windows')
        sequence_systems = [
            system.name
            for system in self.initial.get('systems', [])
        ]

        if systems:
            if system := systems.values_list('name', flat=True).exclude(name__in=sequence_systems).filter(keywords__name=name).first():
                if windows:
                    sequence = self._meta.model.objects.filter(name=name).filter(systems__name=system).filter(windows__in=windows)
                    window = windows.first()

                    if sequence.exists():
                        raise forms.ValidationError(
                            {
                                "name": _(f'Eine Sequenz mit diesem Namen existiert bereits in der Maske "{window.name}"')
                            }
                        )


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
            'systems': ModelSelect2MultipleAdminWidget(
                placeholder=_('System hinzufügen'),
                model=Sequence.systems.through,
                search_fields=['name__icontains'],
            ),
            'windows': Select2MultipleWidget(
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

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if 'quick_change' in request.GET:
            sequence = SequenceQuickChange.objects.get(pk=object_id)
            return HttpResponseRedirect(sequence.get_admin_url() + '?_popup=1' + '#' + request.GET['tab_name'])

        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'systems':
            field = ModelMultipleChoiceField(
                widget=CheckboxSelectMultipleSystems,
                queryset=field.queryset
            )
            field.label = _('Systeme')

            if sequence_id := request.resolver_match.kwargs.get('object_id'):
                sequence = Sequence.objects.get(id=sequence_id)
                window_systems = sequence.windows.values_list('systems', flat=True)
                disabled_systems = System.objects.exclude(pk__in=window_systems)
                field.widget.disabled = set(disabled_systems.values_list('pk', flat=True))

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

        return link(
            window.get_admin_url(),
            window.name,
            new_page=True
        )


class QuickAddSequenceForm(BaseForm):
    def clean(self):
        name = self.cleaned_data.get('name')
        windows = self.cleaned_data.get('windows')

        if len(windows) == 1:
            window = windows[0]
            if window.sequences.filter(name=name).exists():
                raise forms.ValidationError(
                    {
                        "name": _(f'Eine Sequenz mit diesem Namen existiert bereits in der Maske "{window.name}"')
                    }
                )


@admin.register(SequenceQuickAdd)
class SequenceQuickAddAdmin(WindowKeywordAdminMixin, BaseQuickAddAdmin):
    form = QuickAddSequenceForm


class QuickChangeStepsFormset(SequenceStepsFormset):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        # The index of an extra form is None
        if index is None:
            form.fields['to_keyword'].widget.can_add_related = False


class QuickChangeSteps(SequenceSteps):
    formset = QuickChangeStepsFormset


@admin.register(SequenceQuickChange)
class SequenceQuickChangeAdmin(WindowKeywordAdmin):
    fields = []
    readonly_fields = ['documentation']
    inlines = [ParametersInline, QuickChangeSteps]

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
