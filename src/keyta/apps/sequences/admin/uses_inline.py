from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.testcases.models import TestStep
from keyta.widgets import link

from ..models import Sequence


class UsesInline(BaseTabularInline):
    model = TestStep
    fk_name = 'to_keyword'
    fields = ['use']
    readonly_fields = ['use']
    verbose_name_plural = _('Verwendungen')

    def get_queryset(self, request):
        sequence_id = request.resolver_match.kwargs['object_id']
        sequence = Sequence.objects.get(id=sequence_id)
        testcase_to_pk = dict(
            super().get_queryset(request)
            .filter(to_keyword=sequence)
            .values_list('testcase', 'pk')
        )
        pks = list(testcase_to_pk.values())

        return super().get_queryset(request).filter(pk__in=pks).order_by('testcase__name')

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
