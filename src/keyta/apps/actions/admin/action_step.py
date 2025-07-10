from django.contrib import admin

from keyta.apps.keywords.admin import KeywordCallAdmin

from ..models import ActionStep


@admin.register(ActionStep)
class ActionStepAdmin(KeywordCallAdmin):
    pass
