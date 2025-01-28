from django import forms
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext as _

from apps.actions.models import Action
from keyta.widgets import (
    open_link_in_modal,
    BaseSelect
)

from ..models import Execution, SetupTeardown


class SetupTeardownForm(forms.ModelForm):
    def save(self, commit=True):
        setup_teardown: SetupTeardown = super().save(commit)

        if setup_teardown.pk and 'to_keyword' in self.changed_data:
            for param in setup_teardown.parameters.all():
                param.delete()

        return setup_teardown


class SetupTeardownInline(admin.TabularInline):
    model = SetupTeardown
    fields = ['type', 'user', 'to_keyword', 'args']
    form = SetupTeardownForm
    readonly_fields = ['args']
    extra = 1
    max_num = 1
    template = 'admin/setup_teardown/tabular.html'

    @admin.display(description=_('Parameters'))
    def args(self, obj):
        kw_call: SetupTeardown = obj
        to_keyword_has_params = kw_call.to_keyword.parameters.exists()

        if not kw_call.pk or not to_keyword_has_params:
            return '-'

        if ((to_keyword_has_params and not kw_call.parameters.exists()) or
            kw_call.has_empty_arg(self.user)
        ):
            return open_link_in_modal(
                kw_call.get_admin_url(),
                '<i class=" error-duotone fa-solid fa-list" style="font-size: 36px;"></i>'
            )
        else:
            return open_link_in_modal(
                kw_call.get_admin_url(),
                '<i class="fa-solid fa-list" style="font-size: 36px"></i>'
            )

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
