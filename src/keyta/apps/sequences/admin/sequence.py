from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _

from model_clone import CloneModelAdminMixin

from keyta.admin.base_admin import BaseQuickAddAdmin
from keyta.admin.field_documentation import DocumentationField
from keyta.apps.executions.admin import KeywordExecutionInline
from keyta.apps.keywords.admin import (
    ParametersInline,
    ReturnValueInline,
    WindowKeywordAdmin,
    WindowKeywordAdminMixin,
)
from keyta.forms.baseform import BaseForm
from keyta.widgets import ModelSelect2MultipleAdminWidget, Select2MultipleWidget

from ..models import (
    Sequence,
    SequenceQuickAdd,
    SequenceQuickChange
)
from .steps_inline import SequenceSteps


@admin.register(Sequence)
class SequenceAdmin(CloneModelAdminMixin, WindowKeywordAdmin):
    form = forms.modelform_factory(
        Sequence,
        BaseForm,
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
        return ['systems', 'windows'] + super().get_fields(request, obj)

    def get_inlines(self, request, obj):
        sequence: Sequence = obj
        inlines = self.inlines

        if not sequence:
            return [ParametersInline]

        if not sequence.has_empty_sequence:
            return inlines + [ReturnValueInline, KeywordExecutionInline]

        return inlines


@admin.register(SequenceQuickAdd)
class SequenceQuickAddAdmin(WindowKeywordAdminMixin, BaseQuickAddAdmin):
    pass


@admin.register(SequenceQuickChange)
class SequenceQuickChangeAdmin(DocumentationField, WindowKeywordAdmin):
    inlines = [ParametersInline, SequenceSteps, ReturnValueInline]

    def get_fields(self, request, obj=None):
        return ['readonly_documentation']

    def get_readonly_fields(self, request, obj=None):
        return ['readonly_documentation']

    def has_delete_permission(self, request, obj=None):
        return False
