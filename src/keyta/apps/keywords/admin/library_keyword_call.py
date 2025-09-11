from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.widgets import Icon, link

from ..forms import LibraryKeywordCallParameterFormset
from ..models import (
    KeywordCall,
    KeywordCallParameter,
    LibraryKeywordCall,
    LibraryKeywordCallParameter
)
from .keywordcall_conditions_inline import ConditionsInline
from .keywordcall import KeywordCallAdmin, KeywordDocField
from .keywordcall_parameters_inline import KeywordCallParametersInline


class LibraryKeywordCallParametersInline(KeywordCallParametersInline):
    formset = LibraryKeywordCallParameterFormset

    def get_fields(self, request, obj=None):
        if self.has_change_permission(request, obj):
            return super().get_fields(request, obj) + ['reset']
        else:
            return super().get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if self.has_change_permission(request, obj):
            return super().get_readonly_fields(request, obj) + ['reset']
        else:
            return super().get_readonly_fields(request, obj)

    @admin.display(description=_('zurücksetzen'))
    def reset(self, kwcall_parameter: KeywordCallParameter):
        library_kwcall_parameter = LibraryKeywordCallParameter.objects.get(pk=kwcall_parameter.pk)
        url = library_kwcall_parameter.get_admin_url() + '?reset'
        icon =  Icon(
            settings.FA_ICONS.reset_default_value,
            {'font-size': '18px'}
        )

        if library_kwcall_parameter.parameter.default_value:
            return link(url, str(icon))
        else:
            return ''


@admin.register(LibraryKeywordCall)
class LibraryKeywordCallAdmin(
    KeywordDocField,
    KeywordCallAdmin
):
    parameters_inline = LibraryKeywordCallParametersInline

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return self.changeform_view(request, object_id, form_url, extra_context or {'show_delete': False})

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)
        kw_call: KeywordCall = obj

        if kw_call.from_keyword.parameters.exists() or kw_call.get_previous_return_values().exists():
            for condition in kw_call.conditions.all():
                condition.update_expected_value()

            return inlines + [ConditionsInline]

        return inlines
