from django import forms
from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseAddAdmin
from keyta.admin.base_inline import TabularInlineWithDelete
from keyta.forms import form_with_select
from keyta.widgets import ModelSelect2MultipleAdminWidget, Select2MultipleWidget

from apps.executions.admin import KeywordExecutionInline
from keyta.apps.keywords.admin import KeywordDocumentationAdmin
from apps.resources.models import Resource
from apps.windows.admin import (
    WindowKeywordParameters,
    WindowKeywordAdmin,
    WindowKeywordAdminMixin,
    WindowKeywordReturnValues
)

from ..models import (
    SequenceExecution,
    Sequence,
    SequenceDocumentation,
    SequenceResourceImport,
    WindowSequence
)
from .steps_inline import SequenceSteps


class Execution(KeywordExecutionInline):
    model = SequenceExecution


SequenceForm = forms.modelform_factory(
    Sequence,
    forms.ModelForm,
    [],
    widgets={
        'systems': ModelSelect2MultipleAdminWidget(
            model=Sequence.systems.through,
            search_fields=['name__icontains'],
            attrs={
                'data-placeholder': _('System hinzufügen'),
            }
        ),
        'windows': Select2MultipleWidget(
            model=Sequence.windows.through,
            search_fields=['name__icontains'],
            dependent_fields={'systems': 'systems'},
            attrs={
                'data-placeholder': _('Maske auswählen'),
            }
        )
    }
)


class Resources(TabularInlineWithDelete):
    fk_name = 'keyword'
    model = SequenceResourceImport
    fields = ['resource']
    extra = 0
    form = form_with_select(
        SequenceResourceImport,
        'resource',
        _('Ressource auswählen')
    )
    verbose_name = _('Ressource')
    verbose_name_plural = _('Ressourcen')

    def get_max_num(self, request, obj=None, **kwargs):
        return Resource.objects.count()

    def get_field_queryset(self, db, db_field, request: HttpRequest):
        queryset = super().get_field_queryset(db, db_field, request)
        imported_resources = self.get_queryset(request).values_list('resource_id', flat=True)
        return queryset.exclude(id__in=imported_resources)

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


@admin.register(Sequence)
class SequenceAdmin(WindowKeywordAdmin):
    inlines = [
        Resources,
        WindowKeywordParameters,
        SequenceSteps
    ]
    form = SequenceForm

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'systems':
            field.help_text = ''
            field.label = _('Systeme')
            field.widget.can_add_related = False

        if db_field.name == 'windows':
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
            field.widget.can_view_related = False

        return field

    def get_fields(self, request, obj=None):
        return ['systems', 'windows'] + super().get_fields(request, obj)

    def get_inlines(self, request, obj):
        sequence: Sequence = obj

        if not sequence:
            return [WindowKeywordParameters]

        if not sequence.has_empty_sequence:
            return self.inlines + [WindowKeywordReturnValues, Execution]

        return self.inlines


@admin.register(SequenceDocumentation)
class SequenceDocumentationAdmin(KeywordDocumentationAdmin):
    pass


@admin.register(WindowSequence)
class WindowSequenceAdmin(WindowKeywordAdminMixin, BaseAddAdmin):
    pass
