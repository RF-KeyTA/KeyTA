from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models import ActionWindowRelation


@admin.register(ActionWindowRelation)
class ActionWindowRelationAdmin(BaseAdmin):
    def get_protected_objects(self, obj: ActionWindowRelation):
        return obj.keyword.uses.filter(from_keyword__in=obj.window.keywords.all())
