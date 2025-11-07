from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse

from keyta.apps.keywords.admin import (
    KeywordCallAdmin,
    KeywordCallParametersInline,
    ReadOnlyReturnValuesInline
)
from keyta.apps.keywords.forms.keywordcall_parameter_formset import (
    KeywordCallParameterFormsetWithErrors, get_prev_return_values, get_window_variables
)
from keyta.widgets import Icon, open_link_in_modal, url_query_parameters

from ..models import TestStep
from .quick_change_variables_inline import QuickChangeVariables


def get_choices_groups(test_step: TestStep):
    choices = []
    systems = test_step.testcase.systems.all()
    window = test_step.window

    if prev_return_values := get_prev_return_values(test_step):
        choices.append({
            'icon': settings.FA_ICONS.arg_return_value,
            'group': prev_return_values
        })

    if window_variables := get_window_variables(systems, window):
        choices.append({
            'icon': settings.FA_ICONS.arg_variable,
            'group': window_variables
        })

    return choices


class TestStepParameterFormset(KeywordCallParameterFormsetWithErrors):
    def get_choices_groups(self, test_step: TestStep):
        return get_choices_groups(test_step)


class TestStepParametersInline(KeywordCallParametersInline):
    formset = TestStepParameterFormset

    def get_queryset(self, request):
        return super().get_queryset(request).filter(user=request.user)


@admin.register(TestStep)
class TestStepAdmin(
    KeywordCallAdmin
):
    change_form_template = 'test_step_change_form.html'
    # It must be a non-empty list, otherwise the inlines are not shown as tabs.
    inlines = [QuickChangeVariables]
    orig_inlines = [QuickChangeVariables]

    def switch_inlines(self, request):
        if request.method == 'POST':
            self.inlines = []
        else:
            self.inlines = self.orig_inlines

    def change_view(self, request, object_id, form_url="", extra_context=None):
        self.switch_inlines(request)

        test_step = TestStep.objects.get(pk=object_id)

        if _type := request.GET.get('_type') == 'query':
            return JsonResponse({
                'results': self.get_select2_choices(request, test_step, get_choices_groups(test_step))
            })

        if 'step-changed' in request.GET:
            return HttpResponse(open_link_in_modal(
                test_step.to_keyword.get_admin_url() + f'?kw_call_pk={test_step.pk}',
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

        current_app, model, *route = request.resolver_match.route.split('/')
        app = settings.MODEL_TO_APP.get(model)

        if app and app != current_app:
            return HttpResponseRedirect(reverse('admin:%s_%s_change' % (app, model), args=(object_id,)))

        return self.changeform_view(request, object_id, form_url, extra_context or {'show_delete': False})

    def get_inlines(self, request, obj):
        test_step: TestStep = obj
        inlines = []

        if test_step.parameters.exists():
            inlines.append(TestStepParametersInline)
            inlines.extend(self.inlines)

        if test_step.return_values.exists():
            inlines.append(ReadOnlyReturnValuesInline)

        return inlines

    def has_change_permission(self, request, obj=None):
        return True
