from django.utils.translation import gettext as _

from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.apps.resources.admin import ResourceImportsInline
from keyta.apps.resources.models import Resource, ResourceImport
from keyta.forms import form_with_select

from ..models import Sequence


class Resources(DeleteRelatedField, ResourceImportsInline):
    fk_name = 'keyword'
    fields = ['resource']
    form = form_with_select(
        ResourceImport,
        'resource',
        _('Ressource auswählen')
    )

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        sequence: Sequence = obj

        imported_resources = self.get_queryset(request).filter(keyword_id=sequence.pk).values_list('resource_id', flat=True)
        resource_field = formset.form.base_fields['resource']
        resource_field.queryset = resource_field.queryset.exclude(id__in=imported_resources)

        return formset

    def get_max_num(self, request, obj=None, **kwargs):
        return Resource.objects.count()
