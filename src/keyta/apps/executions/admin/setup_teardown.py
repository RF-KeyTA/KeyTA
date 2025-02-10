from django.contrib import admin

from keyta.apps.keywords.admin import KeywordCallAdmin, KeywordCallParametersInline
from keyta.apps.keywords.models import KeywordCall

from ..forms import SetupTeardownParametersFormset
from ..models import Setup, Teardown


class SetupTeardownParametersInline(KeywordCallParametersInline):
    formset = SetupTeardownParametersFormset


@admin.register(Setup)
@admin.register(Teardown)
class SetupTeardownAdmin(KeywordCallAdmin):
    fields = ['keyword_doc']
    readonly_fields = ['keyword_doc']
    inlines = [SetupTeardownParametersInline]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        kw_call = KeywordCall.objects.get(id=object_id)
        kw_call.update_parameters(request.user)
        return super().change_view(request, object_id, form_url, extra_context)
