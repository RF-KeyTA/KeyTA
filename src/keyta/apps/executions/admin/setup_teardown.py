from django.contrib import admin

from keyta.apps.keywords.admin import KeywordCallAdmin

from ..models import SetupTeardown
from .setup_teardown_parameters_inline import  SetupTeardownParametersInline


@admin.register(SetupTeardown)
class SetupTeardownAdmin(KeywordCallAdmin):
    fields = ['keyword_doc']
    readonly_fields = ['keyword_doc']

    def change_view(self, request, object_id, form_url="", extra_context=None):
        setup_teardown = SetupTeardown.objects.get(id=object_id)

        for param in setup_teardown.to_keyword.parameters.all():
            setup_teardown.add_parameter(param, user=request.user)

        return super().change_view(request, object_id, form_url, extra_context)

    def get_inlines(self, request, obj):
        return [
            SetupTeardownParametersInline
        ]
