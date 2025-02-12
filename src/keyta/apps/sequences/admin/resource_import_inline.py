from django.http import HttpRequest
from django.utils.translation import gettext as _

from keyta.admin.base_inline import TabularInlineWithDelete
from keyta.apps.resources.models import Resource
from keyta.forms import form_with_select

from ..models import SequenceResourceImport


class Resources(TabularInlineWithDelete):
    fk_name = 'keyword'
    model = SequenceResourceImport
    fields = ['resource']
    extra = 0
    form = form_with_select(
        SequenceResourceImport,
        'resource',
        _('Ressource auswählen')
    )
    verbose_name = _('Ressource')
    verbose_name_plural = _('Ressourcen')

    def get_max_num(self, request, obj=None, **kwargs):
        return Resource.objects.count()

    def get_field_queryset(self, db, db_field, request: HttpRequest):
        queryset = super().get_field_queryset(db, db_field, request)
        imported_resources = self.get_queryset(request).values_list('resource_id', flat=True)
        return queryset.exclude(id__in=imported_resources)

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False
