from django import template
from os.path import basename

register = template.Library()

@register.filter
def filename(value):
    return basename(value)

@register.filter
def star_range(value):
    return range(value)