from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.widgets import Icon, link

from ..forms import LibraryKeywordCallParameterFormset
from ..forms.keywordcall_parameter_formset import ErrorsMixin
from ..models import KeywordCall, KeywordCallParameter, LibraryKeywordCallParameter
from .keywordcall_parameters_inline import KeywordCallParametersInline


class LibraryKeywordCallParameterFormsetWithErrors(ErrorsMixin, LibraryKeywordCallParameterFormset):
    pass


class LibraryKeywordCallParametersInline(KeywordCallParametersInline):
    formset = LibraryKeywordCallParameterFormsetWithErrors

    def get_fields(self, request, obj=None):
        kw_call: KeywordCall = obj
        fields = super().get_fields(request, obj)

        if kw_call.to_keyword.parameters.filter(default_value__isnull=False).exists():
            LibraryKeywordCallParametersInline.reset = reset

            if self.has_change_permission(request, obj):
                return fields + ['reset']

        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if 'reset' in self.get_fields(request, obj) and self.has_change_permission(request, obj):
                return readonly_fields + ['reset']

        return readonly_fields


@admin.display(description=_('zurücksetzen'))
def reset(self, kwcall_parameter: KeywordCallParameter):
    library_kwcall_parameter = LibraryKeywordCallParameter.objects.get(pk=kwcall_parameter.pk)
    url = library_kwcall_parameter.get_admin_url() + '?reset'
    icon = Icon(
        settings.FA_ICONS.reset_default_value,
        {'font-size': '18px'}
    )

    if library_kwcall_parameter.parameter.default_value:
        return link(url, str(icon))
    else:
        return ''
