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
    if items:
        for item in items:
            total += item['total_price']
        return total
    else:
        return 0    

@register.filter
def total_items(items):
    quantity = 0
    if items:
        for item in items:
            quantity += item['total_quantity']
        return quantity
    else:
        return 0

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def filter(query_params, key):
    return query_params.getlist(key)
