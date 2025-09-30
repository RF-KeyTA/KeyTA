from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.keywords.admin.field_keywordcall_values import KeywordCallValuesField
from keyta.apps.keywords.forms import StepsForm
from keyta.apps.keywords.models import Keyword
from keyta.forms.baseform import form_with_select

from ..models import Execution, Setup, Teardown


class SetupTeardownKeywordCallValuesField(KeywordCallValuesField):
    def get_user(self, request):
        return request.user


class SetupInline(SetupTeardownKeywordCallValuesField, BaseTabularInline):
    model = Setup
    fields = ['enabled', 'to_keyword']
    form = form_with_select(
        Setup,
        'to_keyword',
        _('Aktion auswählen'),
        labels={
            'to_keyword': _('Aktion')
        },
        form_class=StepsForm
    )
    extra = 0
    max_num = 1

    def get_formset(self, request: HttpRequest, obj=None, **kwargs):
        execution: Execution = obj
        systems = QuerySet()

        if keyword := execution.keyword:
            systems = keyword.systems.all()

        if testcase := execution.testcase:
            systems = testcase.systems.all()

        keywords = (
            Keyword.objects
            .filter(systems__in=systems)
            .filter(setup_teardown=True)
            .distinct()
        )

        if keyword:
            keywords = keywords.exclude(pk=execution.keyword.pk)

        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['to_keyword'].queryset = keywords

        return formset


class TeardownInline(SetupInline):
    model = Teardown
    verbose_name = _('Nachbereitung')
