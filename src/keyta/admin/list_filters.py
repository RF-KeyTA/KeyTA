from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class SystemListFilter(admin.RelatedFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)

        self.title = _('System')

    @property
    def include_empty_choice(self):
        return False


class DependentListFilter(admin.RelatedFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)

        query_params = {
            self.dependent_field: id
            for param, id in request.GET.items()
            if param.startswith(self.dependent_field)
        }

        if query_params:
            dep_field = self.dependent_field
            filter = {dep_field + '__in': query_params[dep_field]}
            self.lookup_choices = (
                field.related_model.objects
                .filter(**filter)
                .values_list('id', 'name')
            )


class WindowListFilter(DependentListFilter):
    dependent_field = 'systems'

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)

        self.empty_value_display = _('Masken-unabhängig')
        self.title = _('Maske')
