from django.contrib import admin
from django.http import HttpRequest

from keyta.apps.keywords.admin import KeywordCallAdmin, KeywordCallParametersInline
from keyta.apps.keywords.admin.field_keyword_documentation import KeywordDocField
from keyta.apps.keywords.models import KeywordCall

from ..forms import SetupTeardownParametersFormset
from ..models import Setup, Teardown


class SetupTeardownParametersInline(KeywordCallParametersInline):
    fields = ['name', 'value']
    formset = SetupTeardownParametersFormset

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).filter(user=request.user)


@admin.register(Setup)
@admin.register(Teardown)
class SetupTeardownAdmin(
    KeywordDocField,
    KeywordCallAdmin
):
    def change_view(self, request, object_id, form_url="", extra_context=None):
        kw_call = KeywordCall.objects.get(pk=object_id)

        if request.GET.get('update-icon'):
            return self.update_icon(request, kw_call)

        kw_call.update_parameter_values()

        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_inlines(self, request, obj):
        setup: Setup = obj

        if setup.parameters.exists():
            return [SetupTeardownParametersInline]

        return []
