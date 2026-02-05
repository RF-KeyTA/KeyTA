from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def icon(name):
    return getattr(settings.FA_ICONS, name)
