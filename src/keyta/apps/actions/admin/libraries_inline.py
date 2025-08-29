from django.utils.translation import gettext_lazy as _

from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.apps.libraries.admin import LibraryImportInline
from keyta.apps.libraries.models import Library, LibraryImport
from keyta.forms.baseform import form_with_select

from ..models import Action


class Libraries(DeleteRelatedField, LibraryImportInline):
    fk_name = 'keyword'
    fields = ['library']
    form = form_with_select(
        LibraryImport,
        'library',
        _('Bibliothek auswählen')
    )
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        action: Action = obj

        imported_libraries = (
            self.get_queryset(request)
            .filter(keyword_id=action.pk)
            .values_list('library_id', flat=True)
        )
        library_field = formset.form.base_fields['library']
        library_field.queryset = library_field.queryset.exclude(id__in=imported_libraries)

        return formset

    def get_max_num(self, request, obj=None, **kwargs):
        return Library.objects.count()

    def has_delete_permission(self, request, obj=None):
        return self.can_change(request.user, 'action')
