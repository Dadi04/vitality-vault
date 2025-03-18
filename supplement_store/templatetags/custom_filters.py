from django import template
from os.path import basename
import urllib.parse

register = template.Library()

@register.filter
def filename(value):
    return basename(str(value))

@register.filter
def change(value):
    if isinstance(value, str):
        return value.replace('%', '_')
    return value

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

@register.filter
def total_items(items):
    quantity = 0
    if not items:
        return quantity
    
    try:
        if items[0].get('total_quantity'):
            for item in items:
                quantity += item.get('total_quantity')
        else:
            quantity = len(items)
    except (AttributeError, TypeError):
        if hasattr(items[0], 'total_quantity') and items[0].total_quantity:
            for item in items:
                quantity += item.total_quantity
        else:
            quantity = len(items)
    return quantity

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def filter(query_params, key):
    return query_params.getlist(key)

@register.filter
def urlencode(param):
    return urllib.parse.quote(param)