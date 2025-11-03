from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from admin.field_execution_state import ExecutionStateField
from keyta.admin.base_inline import SortableTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.apps.keywords.admin.field_keywordcall_values import KeywordCallValuesField
from keyta.apps.keywords.forms import StepsForm
from keyta.apps.keywords.models import Keyword, KeywordType
from keyta.apps.windows.models import Window
from keyta.widgets import ModelSelect2AdminWidget

from ..forms import TestStepsFormset
from ..models import TestCase, TestStep


class TestStepValuesField(KeywordCallValuesField):
    def get_user(self, request):
        return request.user


class TestStepsInline(
    ExecutionStateField,
    DeleteRelatedField,
    TestStepValuesField,
    SortableTabularInline
):
    model = TestStep
    fk_name = 'testcase'
    fields = ['test_step_url', 'execution_state', 'window', 'to_keyword']
    readonly_fields = ['test_step_url']
    extra = 0 # necessary for saving, since to_keyword is not nullable and is null in an extra
    form = StepsForm
    formset = TestStepsFormset
    template = 'test_steps_sortable_tabular.html'

    @admin.display(description='')
    def test_step_url(self, obj):
        test_step: TestStep = obj

        return test_step.get_admin_url()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        testcase_id = request.resolver_match.kwargs['object_id']
        testcase = TestCase.objects.get(id=testcase_id)

        if db_field.name == 'to_keyword':
            field.label = _('Sequenz')
            field.queryset = field.queryset.filter(Q(type=KeywordType.SEQUENCE) | Q(resource__isnull=False))
            field.widget.widget = ModelSelect2AdminWidget(
                placeholder=_('Sequenz auswählen'),
                model=Keyword,
                search_fields=['name__icontains'],
                dependent_fields={'window': 'windows'},
                attrs={'data-allow-clear': 'true'}
            )

        if db_field.name == 'window':
            field.queryset = field.queryset.filter(systems__in=testcase.systems.all()).distinct()
            field.widget.widget = ModelSelect2AdminWidget(
                placeholder=_('Maske auswählen'),
                model=Window,
                search_fields=['name__icontains']
            )

        return field

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('to_keyword')
            .prefetch_related('to_keyword__parameters')
            .prefetch_related('to_keyword__return_values')
        )

    def has_delete_permission(self, request, obj=None):
        return self.can_change(request.user, 'testcase')
