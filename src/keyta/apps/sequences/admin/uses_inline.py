from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.testcases.models import TestStep
from keyta.widgets import link


class UsesInline(BaseTabularInline):
    model = TestStep
    fk_name = 'to_keyword'
    fields = ['use']
    readonly_fields = ['use']
    verbose_name_plural = _('Verwendungen')

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('testcase__name')

    def has_add_permission(self, request, obj):
        return False

    @admin.display(description=_('Testfall'))
    def use(self, obj):
        test_step: TestStep = obj

        return link(
            test_step.testcase.get_admin_url(),
            test_step.testcase.name,
            new_page=True
        )
