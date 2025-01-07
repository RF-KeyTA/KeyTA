from django import forms
from django.contrib import admin
from django.utils.translation import gettext as _

from apps.common.admin import SortableTabularInlineWithDelete
from apps.common.widgets import open_link_in_modal
from ..models import KeywordCall, Keyword


class StepsForm(forms.ModelForm):
    def save(self, commit=True):
        kw_call: KeywordCall = super().save(commit)

        if kw_call.pk and 'to_keyword' in self.changed_data:
            to_keyword: Keyword = self.cleaned_data['to_keyword']

            for param in kw_call.parameters.all():
                param.delete()

            for param in to_keyword.parameters.all():
                kw_call.add_parameter(param)

        return kw_call


class StepsInline(SortableTabularInlineWithDelete):
    model = KeywordCall
    fields = ['to_keyword', 'first_arg', 'args']
    form = StepsForm
    readonly_fields = ['first_arg', 'args']
    extra = 1  # Must be > 0 in order for SequenceSteps to work

    @admin.display(description=_('Werte'))
    def args(self, obj):
        kw_call: KeywordCall = obj

        if not kw_call.pk:
            return '-'

        if kw_call.has_empty_arg():
            return open_link_in_modal(
                kw_call.get_admin_url(),
                '<i class=" error-duotone fa-solid fa-list" style="font-size: 36px;"></i>'
            )
        else:
            return open_link_in_modal(
                kw_call.get_admin_url(),
                '<i class=" fa-solid fa-list" style="font-size: 36px"></i>'
            )

    @admin.display(description=_('1. Parameter'))
    def first_arg(self, obj: KeywordCall):
        return obj.parameters.first().current_value or "-"
