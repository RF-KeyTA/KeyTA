from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from jinja2 import Template

from keyta.widgets import Icon


class ExecutionStateField:
    icon = Icon(
        settings.FA_ICONS.execute,
        styles={'font-size': '18px', 'margin-left': '12px'},
        title=_('Ausführen')
    )

    @admin.display(description=mark_safe(str(icon)))
    def exec_state(self, obj):
        step = obj
        idx = step.index

        template = """
        <select name="steps-{{idx}}-execution_state" id="id_steps-{{idx}}-execution_state" tabindex="-1" aria-hidden="true">
            <option value="EXECUTE" selected="" data-select2-id="select2-data-2-f8ae">EXECUTE</option>
            <option value="SKIP_EXECUTION">SKIP_EXECUTION</option>
            <option value="BEGIN_EXECUTION">BEGIN_EXECUTION</option>
            <option value="END_EXECUTION">END_EXECUTION</option>
        </select>
        <script>
            function status(value) {
                const status_icon = {
                   'EXECUTE': "{{icon_execute}}",
                   'SKIP_EXECUTION': "{{icon_skip_execution}}",
                   'BEGIN_EXECUTION': "{{icon_begin_execution}}",
                   'END_EXECUTION': "{{icon_end_execution}}"
                };

                return status_icon[value];
            }

            function translate(value) {
                const translate = {
                    'EXECUTE': "{{execute}}",
                    'SKIP_EXECUTION': "{{skip_execution}}",
                    'BEGIN_EXECUTION': "{{begin_execution}}",
                    'END_EXECUTION': "{{end_execution}}",
                }

                return translate[value];
            }

            function formatResult(data) {
                const template = '<span title="' + translate(data.text) + '"><i class="' + status(data.text) + '"></i></span>'
                return $(template)
            }

            function formatSelection(data) {
                const $template = django.jQuery('<span title="' + translate(data.text) + '"><i></i><span></span></span>')
                $template.find('i').addClass(status(data.text))
                return $template
            }

            django.jQuery('#id_steps-{{idx}}-execution_state').select2({
                minimumResultsForSearch: Infinity,
                templateResult: formatResult,
                templateSelection: formatSelection,
                width: 'element'
            })
        </script>
        """

        data = {
            'idx': idx,
            'execute': _('Ausführen'),
            'skip_execution': _('Überspringen'),
            'begin_execution': _('Ausführen ab'),
            'end_execution': _('Ausführen bis'),
            'icon_execute': settings.FA_ICONS.step_execute,
            'icon_skip_execution': settings.FA_ICONS.step_skip_execution,
            'icon_begin_execution': settings.FA_ICONS.step_begin_execution,
            'icon_end_execution': settings.FA_ICONS.step_end_execution
        }

        return mark_safe(Template(template).render(**data))

    def get_fields(self, request, obj=None):
        return ['exec_state'] + super().get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        return ['exec_state'] + super().get_readonly_fields(request, obj)
