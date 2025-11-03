from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from jinja2 import Template

from keyta.widgets import Icon


class ExecutionStateField:
    @admin.display(description=mark_safe(str(Icon(
        settings.FA_ICONS.execute,
        styles={'font-size': '18px', 'margin-left': '12px'},
        title=_('Ausführen')
    ))))
    def exec_state(self, obj):
        step = obj
        idx = step.index
        options = {
            'EXECUTE': {'icon': settings.FA_ICONS.step_execute, 'title': _('Ausführen')},
            'SKIP_EXECUTION': {'icon': settings.FA_ICONS.step_skip_execution, 'title': _('Überspringen')},
            'BEGIN_EXECUTION': {'icon': settings.FA_ICONS.step_begin_execution, 'title': _('Ausführen ab')},
            'END_EXECUTION': {'icon': settings.FA_ICONS.step_end_execution, 'title': _('Ausführen bis')},
        }
        data = {
            'idx': idx,
            'options': options
        }
        template = """
        <select name="steps-{{idx}}-execution_state" id="id_steps-{{idx}}-execution_state" tabindex="-1" aria-hidden="true">
            {% for option in options %}
            <option value="{{ option }}" {% if option == 'EXECUTE' %}selected{% endif %}>{{ option }}</option>
            {% endfor %}
        </select>
        <script>
            function options(option) {
                const options = {{ options }}
                return options[option]
            }

            function formatResult(data) {
                const option = options(data.text)
                if (!option) return data.text
                
                const template = '<span title="' + option.title + '"><i class="' + option.icon + '"></i></span>'
                return $(template)
            }

            function formatSelection(data) {
                const option = options(data.text)
                if (!option) return data.text
                
                const $template = django.jQuery('<span title="' + option.title + '"><i></i><span></span></span>')
                $template.find('i').addClass(option.icon)
                return $template
            }

            django.jQuery('#id_steps-{{idx}}-execution_state').select2({
                minimumResultsForSearch: Infinity,
                templateResult: formatResult,
                templateSelection: formatSelection,
                width: 'element'
            })
            
            django.jQuery('#id_steps-{{idx}}-execution_state').on('change', function (event) {
                const value = $(event.target).val()
                const id = $(event.target).attr('id')
                const selects = $('select[id$="execution_state"]')
            
                if (value === 'BEGIN_EXECUTION') {
                    selects.each((index, select) => {
                        const otherSelect = django.jQuery(select)
                    
                        if (otherSelect.val() === 'BEGIN_EXECUTION' && otherSelect.attr('id') !== id) {
                            otherSelect.val('EXECUTE')
                            otherSelect.trigger('change')
                        }
                    })
                }

                if (value === 'END_EXECUTION') {
                    selects.each((index, select) => {
                        const otherSelect = django.jQuery(select)
                    
                        if (otherSelect.val() === 'END_EXECUTION' && otherSelect.attr('id') !== id) {
                            otherSelect.val('EXECUTE')
                            otherSelect.trigger('change')
                        }
                    })
                }
            })
        </script>
        """

        return mark_safe(Template(template).render(**data))

    def get_fields(self, request, obj=None):
        return ['exec_state'] + super().get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        return ['exec_state'] + super().get_readonly_fields(request, obj)
