from typing import Optional

from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.keywords.admin.field_keywordcall_args import BaseKeywordCallArgs
from keyta.apps.keywords.forms import StepsForm
from keyta.apps.keywords.models import Keyword
from keyta.forms.baseform import form_with_select

from ..models import Execution, Setup, Teardown


class KeywordCallUserArgsField(BaseKeywordCallArgs):
    def invalid_keyword_call_args(self, kw_call: Setup, user: Optional[AbstractUser]=None) -> bool:
        return kw_call.has_empty_arg(user)

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj) + ['args']

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        @admin.display(description=_('Werte'))
        def args(self, kw_call: Setup):
            if kw_call.to_keyword.parameters.exists():
                return self.get_icon(kw_call, request.user)
            else:
                return '-'

        KeywordCallUserArgsField.args = args

        return super().get_readonly_fields(request, obj) + ['args']


class SetupInline(KeywordCallUserArgsField, BaseTabularInline):
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
    extra = 1
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

        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['to_keyword'].queryset = keywords

        return formset


class TeardownInline(SetupInline):
    model = Teardown
    verbose_name = _('Nachbereitung')
