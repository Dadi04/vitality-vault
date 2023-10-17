from django import template
from os.path import basename

register = template.Library()

@register.filter
def filename(value):
    return basename(value)

@register.filter
def star_range(value):
    return range(value)

@register.filter
def total_price(items):
    total = 0
    for item in items:
        total += item.item.price * item.quantity
    return total