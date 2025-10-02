from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.keywords.admin.field_keywordcall_values import KeywordCallValuesField
from keyta.apps.keywords.forms import StepsForm
from keyta.apps.keywords.models import Keyword
from keyta.widgets import ModelSelect2AdminWidget

from ..forms import SetupTeardownFormset
from ..models import Execution, Setup, Teardown


class SetupTeardownKeywordCallValuesField(KeywordCallValuesField):
    def get_user(self, request):
        return request.user


class SetupInline(SetupTeardownKeywordCallValuesField, BaseTabularInline):
    model = Setup
    fields = ['enabled', 'to_keyword']
    form = StepsForm
    formset = SetupTeardownFormset
    extra = 0
    max_num = 1

    def formfield_for_dbfield(self, db_field, request: HttpRequest, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        execution_id = request.resolver_match.kwargs['object_id']
        execution = Execution.objects.get(id=execution_id)

        if db_field.name == 'to_keyword':
            queryset = field.queryset.filter(setup_teardown=True)
            systems = QuerySet()

            if keyword := execution.keyword:
                systems = keyword.systems.all()
                queryset = queryset.exclude(pk=keyword.pk)

            if testcase := execution.testcase:
                systems = testcase.systems.all()

            field.label = _('Aktion')
            field.queryset = queryset.filter(systems__in=systems).distinct()
            field.widget.widget = ModelSelect2AdminWidget(
                placeholder=_('Aktion auswählen'),
                model=Keyword,
                search_fields=['name__icontains']
            )

        return field


class TeardownInline(SetupInline):
    model = Teardown
    verbose_name = _('Nachbereitung')
