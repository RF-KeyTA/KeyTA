from django import forms
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext as _

from keyta.apps.actions.models import Action
from keyta.apps.keywords.admin import KeywordCallArgsField
from keyta.widgets import BaseSelect


from ..forms import SetupTeardownForm
from ..models import Execution, Setup, Teardown


class SetupInline(KeywordCallArgsField, admin.TabularInline):
    model = Setup
    fields = ['user', 'to_keyword', 'args']
    form = SetupTeardownForm
    readonly_fields = ['args']
    extra = 0
    max_num = 1
    template = 'admin/setup_teardown/tabular.html'

    @admin.display(description=_('Parameters'))
    def args(self, kw_call: Setup):
        to_keyword_has_params = kw_call.to_keyword.parameters.exists()

        if not kw_call.pk or not to_keyword_has_params:
            return '-'
        else:
            return super().args(kw_call)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'user':
            field.initial = request.user
            field.widget = forms.HiddenInput()

        return field

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        execution: Execution = obj
        systems = QuerySet()

        if keyword := execution.keyword:
            systems = keyword.systems.all()
        if testcase := execution.testcase:
            systems = testcase.systems.all()

        queryset = (
            Action.objects
            .filter(systems__in=systems)
            .filter(setup_teardown=True)
            .distinct()
        )
        formset.form.base_fields['to_keyword'].queryset = queryset
        formset.form.base_fields['to_keyword'].label = _('Aktion')
        formset.form.base_fields['to_keyword'].widget = BaseSelect(
            _('Aktion auswählen')
        )

        return formset

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        return queryset.filter(user=request.user)

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        self.user = request.user
        return self.readonly_fields


class TeardownInline(SetupInline):
    model = Teardown
    verbose_name = _('Nachbereitung')
