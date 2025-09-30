from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse

from keyta.apps.keywords.admin.keywordcall import (
    KeywordCallAdmin,
    KeywordCallParametersInline
)
from keyta.apps.keywords.forms import KeywordCallParameterFormsetWithErrors
from keyta.apps.keywords.forms.keywordcall_parameter_formset import (
    get_prev_return_values,
    get_variables_choices
)
from keyta.apps.keywords.models import KeywordCall
from keyta.apps.variables.models import Variable
from keyta.widgets import Icon, open_link_in_modal, url_query_parameters

from ..models import TestStep


def get_window_variables(kw_call: KeywordCall):
    variables = (
        Variable.objects
        .filter(
            windows__in=[kw_call.window],
            systems__in=kw_call.testcase.systems.all()
        )
    )

    return get_variables_choices(variables)


class TestStepParameterFormset(KeywordCallParameterFormsetWithErrors):
    def get_ref_choices(self, kw_call: KeywordCall):
        return get_prev_return_values(kw_call) + get_window_variables(kw_call)


class TestStepParametersInline(KeywordCallParametersInline):
    fields = ['name', 'value']
    formset = TestStepParameterFormset


@admin.register(TestStep)
class TestStepAdmin(
    KeywordCallAdmin
):
    parameters_inline = TestStepParametersInline

    def change_view(self, request, object_id, form_url="", extra_context=None):
        test_step = TestStep.objects.get(pk=object_id)

        if 'step-changed' in request.GET:
            return HttpResponse(open_link_in_modal(
                test_step.to_keyword.get_admin_url(),
                str(Icon('fa-solid fa-magnifying-glass', {'font-size': '16px'})),
                attrs={
                    'data-href-template': '/keywords/keyword/__fk__/change/?_to_field=id&_popup=1'
                }
            ))

        if 'step-empty' in request.GET:
            query_params = {
                'systems': test_step.testcase.systems.first().pk,
                'windows': test_step.window.pk
            }

            return HttpResponse(open_link_in_modal(
                reverse('admin:sequences_sequencequickadd_add') + '?' + url_query_parameters(query_params),
                str(Icon('fa-solid fa-circle-plus mr-2', {'font-size': '16px'})),
                attrs={
                    'data-href-template': '/keywords/keyword/__fk__/change/?_to_field=id&_popup=1'
                }
            ))

        if 'update-icon' in request.GET:
            return self.update_icon(request, test_step)

        return self.changeform_view(request, object_id, form_url, extra_context or {'show_delete': False})
