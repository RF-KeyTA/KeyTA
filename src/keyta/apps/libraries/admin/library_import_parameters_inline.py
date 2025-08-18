from django.conf import settings
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from keyta.widgets import link, Icon

from ..models import LibraryImportParameter
from .library_parameters_inline import LibraryParametersInline


class LibraryImportParametersInline(LibraryParametersInline):
    model = LibraryImportParameter
    prefetch_related = 'library_import'
    verbose_name_plural = _('Einstellungen')

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        queryset: QuerySet = super().get_queryset(request)
        return queryset.filter(user=request.user)

    def name(self, kwarg: LibraryImportParameter):
        return str(kwarg)

    @admin.display(description=_('zurücksetzen'))
    def reset(self, lib_param: LibraryImportParameter):
        url = lib_param.get_admin_url() + '?reset'
        icon =  Icon(
            settings.FA_ICONS.reset_default_value,
            {'font-size': '18px'}
        )

        return link(url, str(icon))
