from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.keywords.models import KeywordWindowRelation


class WindowKeywordInline(BaseTabularInline):
    model = KeywordWindowRelation
    readonly_fields = ['systems']

    @admin.display(description=_('Systeme'))
    def systems(self, obj: KeywordWindowRelation):
        return ', '.join(obj.keyword.systems.values_list('name', flat=True))

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .prefetch_related('keyword')
            .order_by('keyword__name')
        )

    def has_change_permission(self, request, obj=None):
        return False
