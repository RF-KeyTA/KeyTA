from keyta.apps.keywords.models import KeywordCall
from keyta.widgets import Icon, open_link_in_modal

from project.settings import FAIcons


class KeywordCallArgsField(object):
    def args(self, kw_call: KeywordCall):
        if kw_call.has_empty_arg():
            icon = Icon(
                FAIcons.kw_call_parameters,
                {'filter': 'hue-rotate(150deg)'}
            )

            return open_link_in_modal(
                kw_call.get_admin_url(),
                str(icon)
            )
        else:
            icon = Icon(
                FAIcons.kw_call_parameters
            )

            return open_link_in_modal(
                kw_call.get_admin_url(),
                str(icon)
            )
