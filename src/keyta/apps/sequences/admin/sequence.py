from django import forms
from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext as _


from apps.common.admin import BaseAddAdmin, TabularInlineWithDelete
from apps.common.forms import form_with_select
from apps.common.widgets import ModelSelect2MultipleAdminWidget, Select2MultipleWidget
from apps.executions.admin import KeywordExecutionInline
from apps.keywords.admin import KeywordDocumentationAdmin
from apps.windows.admin import (
    WindowKeywordParameters,
    WindowKeywordAdmin,
    WindowKeywordReturnValues
)
from .steps_inline import SequenceSteps

from ..models import (
    SequenceExecution,
    Sequence,
    SequenceDocumentation,
    SequenceResourceImport,
    WindowSequence
)


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

    def has_change_permission(self, request: HttpRequest, obj) -> bool:
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
class WindowSequenceAdmin(BaseAddAdmin):
    pass
