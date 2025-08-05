from django import forms
from django.contrib import admin
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
from keyta.forms.baseform import BaseForm
from keyta.apps.windows.models import Window
from keyta.widgets import (
    ModelSelect2MultipleAdminWidget, 
    Select2MultipleWidget, 
    link
)

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

        if self.instance:
            window = self.instance.windows.first()
            sequence = window.sequences.exclude(name=self.initial.get('name')).filter(name=name)
        else:
            window = self.cleaned_data.get('windows').first()
            sequence = window.sequences.filter(name=name)

        if sequence.exists():
            raise forms.ValidationError(
                {
                    "name": _(f'Eine Sequenz mit diesem Namen existiert bereits in der Maske "{window}"')
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
            return HttpResponseRedirect(sequence.get_admin_url())

        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)

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

    def get_readonly_fields(self, request, obj):
        sequence: Sequence = obj

        if sequence and (sequence.calls.exists() or sequence.uses.filter(testcase__isnull=False).exists()):
            return ['window']
        
        return super().get_readonly_fields(request, obj)

    @admin.display(description=_('Maske'))
    def window(self, sequence: Sequence):
        window: Window = sequence.windows.first()

        return link(
            window.get_admin_url(),
            window.name
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


@admin.register(SequenceQuickChange)
class SequenceQuickChangeAdmin(WindowKeywordAdmin):
    fields = []
    readonly_fields = ['documentation']
    inlines = [ParametersInline, SequenceSteps]

    def get_inlines(self, request, obj):
        sequence: Sequence = obj
        inlines = [*self.inlines]

        kw_call_pks = sequence.calls.values_list('pk')
        if KeywordCallReturnValue.objects.filter(keyword_call__in=kw_call_pks).exists():
            inlines += [ReturnValueInline]

        return inlines

    def has_delete_permission(self, request, obj=None):
        return False
