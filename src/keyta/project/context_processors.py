from django.conf import settings


def icons(request):
    """
    This context processor allows using settings in a template.

    It is used in: templates/admin/base.html
    """

    return {
        'kw_call_drag_handle_icon': settings.FA_ICONS.kw_call_drag_handle
    }
