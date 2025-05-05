from django.contrib import admin
from django.utils.translation import gettext as _


class SystemListFilter(admin.RelatedFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)

        self.title = _('System')

    @property
    def include_empty_choice(self):
        return False


class WindowListFilter(admin.RelatedFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)

        self.empty_value_display = _('Masken-unabhängig')
        self.title = _('Maske')
