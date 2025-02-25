from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext as _

from keyta.apps.keywords.admin import KeywordCallAdmin, KeywordCallParametersInline
from keyta.apps.keywords.models import KeywordCall

from ..forms import SetupTeardownParametersFormset
from ..models import Setup, Teardown


class SetupTeardownParametersInline(KeywordCallParametersInline):
    formset = SetupTeardownParametersFormset

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).filter(user=request.user)


@admin.register(Setup)
@admin.register(Teardown)
class SetupTeardownAdmin(KeywordCallAdmin):
    fields = ['to_keyword_doc']
    readonly_fields = ['to_keyword_doc']
    inlines = [SetupTeardownParametersInline]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        kw_call = KeywordCall.objects.get(pk=object_id)
        kw_call.update_parameters(request.user)

        return super().change_view(request, object_id, form_url, extra_context)

    def get_inlines(self, request, obj):
        return [SetupTeardownParametersInline]

    @admin.display(description=_('Aktion'))
    def to_keyword_doc(self, kw_call: KeywordCall):
        return super().to_keyword_doc(kw_call)
