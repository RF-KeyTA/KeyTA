from django.contrib import admin
from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect

from ..models import LibraryKeywordCallParameter


@admin.register(LibraryKeywordCallParameter)
class LibraryKeywordCallParameterAdmin(admin.ModelAdmin):
    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        if 'reset' in request.GET:
            lib_kwcall_param = LibraryKeywordCallParameter.objects.get(id=object_id)
            lib_kwcall_param.reset_value()

            super().change_view(request, object_id, form_url, extra_context)

            return HttpResponseRedirect(lib_kwcall_param.keyword_call.get_admin_url())

        return super().change_view(request, object_id, form_url, extra_context)
