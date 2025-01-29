from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.widgets import open_link_in_modal
from keyta.apps.keywords.admin import KeywordCallAdmin, KeywordCallParametersInline
from keyta.apps.keywords.forms import KeywordCallParameterFormset
from keyta.apps.keywords.models import KeywordCall


from ..models import ActionCall


class ActionCallParameterFormset(KeywordCallParameterFormset):
    def get_choices(self, obj):
        kw_call: KeywordCall = obj
        system_ids = list(
            kw_call.from_keyword.systems.values_list('pk', flat=True)
        )
        window_ids = list(
            kw_call.from_keyword.windows.values_list('pk', flat=True)
        )

        return super().get_choices(obj) + super().get_variables(
                window_ids,
                system_ids,
                lambda value_ref: str(value_ref)
            )


class ActionCallParametersInline(KeywordCallParametersInline):
    formset = ActionCallParameterFormset


@admin.register(ActionCall)
class ActionCallAdmin(KeywordCallAdmin):
    def get_inlines(self, request, obj):
        action_call: ActionCall = obj

        if action_call.parameters.exists():
            return [ActionCallParametersInline]
        else:
            return []

    @admin.display(description=_('Aktion'))
    def keyword_doc(self, obj: ActionCall):
        return open_link_in_modal(
            obj.to_keyword.get_docadmin_url(),
            obj.to_keyword.name
        )
