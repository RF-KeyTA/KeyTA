from django import forms
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.keywords.admin.field_keywordcall_args import KeywordCallArgsField
from keyta.apps.keywords.forms import StepsForm
from keyta.apps.keywords.models import Keyword
from keyta.forms.baseform import form_with_select

from ..models import Execution, Setup, Teardown


class SetupInline(KeywordCallArgsField, BaseTabularInline):
    model = Setup
    fields = ['enabled', 'user', 'to_keyword']
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

    @admin.display(description=_('Werte'))
    def args(self, setup: Setup):
        if setup.to_keyword.parameters.exists():
            return super().args(setup)
        
        return '-'

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
        formset.form.base_fields['user'].initial = request.user
        formset.form.base_fields['user'].widget = forms.HiddenInput()

        return formset

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).filter(user=request.user)


class TeardownInline(SetupInline):
    model = Teardown
    verbose_name = _('Nachbereitung')
