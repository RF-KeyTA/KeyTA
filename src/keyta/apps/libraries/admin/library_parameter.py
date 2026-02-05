from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect

from ..models import LibraryParameter


@admin.register(LibraryParameter)
class LibraryParameterAdmin(admin.ModelAdmin):
    def change_view(self, request: HttpRequest, object_id, form_url="",
                    extra_context=None):
        if 'reset' in request.GET:
            LibraryParameter.objects.get(id=object_id).reset_value()
            super().change_view(request, object_id, form_url, extra_context)

            return HttpResponseRedirect(request.GET['ref'])

        return super().change_view(request, object_id, form_url, extra_context)
