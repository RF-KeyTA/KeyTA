from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.forms.optional_argument import OptionalArgumentFormSet
from keyta.widgets import Icon, link

from ..models import LibraryParameter


class LibraryParameterFormSet(OptionalArgumentFormSet):
    value_field = 'default_value'


class InitArguments(BaseTabularInline):
    model = LibraryParameter
    fields = ['name', 'default_value', 'reset']
    readonly_fields = ['name', 'reset']
    formset = LibraryParameterFormSet
    extra = 0
    max_num = 0
    can_delete = False

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('library')

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description=_('zurücksetzen'))
    def reset(self, lib_param: LibraryParameter):
        ref = '&ref=' + lib_param.library.get_admin_url() + lib_param.get_tab_url()
        url = lib_param.get_admin_url() + '?reset' + ref
        icon =  Icon(
            settings.FA_ICONS.library_setting_reset,
            {'font-size': '18px'}
        )

        return link(url, str(icon))
