from django.utils.translation import gettext as _

from keyta.admin.base_inline import SortableTabularInlineWithDelete

from ..models import KeywordParameter


class ParametersInline(SortableTabularInlineWithDelete):
    model = KeywordParameter
    fields = ['position', 'name']
    extra = 0
    verbose_name = _('Parameter')
    verbose_name_plural = _('Parameters')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'name':
            field.widget.attrs.update({'style': 'width: 100%'})

        return field
