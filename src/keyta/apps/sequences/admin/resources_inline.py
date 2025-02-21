from django.utils.translation import gettext as _

from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.apps.resources.admin import ResourceImportsInline
from keyta.apps.resources.models import Resource, ResourceImport
from keyta.forms import form_with_select


class Resources(DeleteRelatedField, ResourceImportsInline):
    fk_name = 'keyword'
    fields = ['resource']
    form = form_with_select(
        ResourceImport,
        'resource',
        _('Ressource auswählen')
    )

    def get_field_queryset(self, db, db_field, request):
        queryset = super().get_field_queryset(db, db_field, request)
        imported_resources = self.get_queryset(request).values_list('resource_id', flat=True)
        return queryset.exclude(id__in=imported_resources)

    def get_max_num(self, request, obj=None, **kwargs):
        return Resource.objects.count()
