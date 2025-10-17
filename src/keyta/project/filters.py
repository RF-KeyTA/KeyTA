from django import template

register = template.Library()


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def filter(seq, key_value):
    key, value = key_value.split(',')

    return [
        dic
        for dic in seq
        if value in dic.get(key)
    ]
