from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect

from ..models import LibraryImportParameter


@admin.register(LibraryImportParameter)
class LibraryImportParameterAdmin(admin.ModelAdmin):
    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        if 'reset' in request.GET:
            lib_import_param = LibraryImportParameter.objects.get(id=object_id)
            lib_import_param.reset_value()

            super().change_view(request, object_id, form_url, extra_context)

            return HttpResponseRedirect(lib_import_param.library_import.get_admin_url())

        return super().change_view(request, object_id, form_url, extra_context)
