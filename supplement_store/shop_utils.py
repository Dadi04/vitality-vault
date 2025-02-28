from django.db.models.functions import Coalesce
from django.db.models import Avg, Q, Count

from .models import Review

def apply_sorting(queryset, sort_option):
    if sort_option in ['priceasc', 'pricedesc']:
        queryset = queryset.annotate(effective_price=Coalesce('sale_price', 'price'))
        if sort_option == 'priceasc':
            queryset = queryset.order_by('-is_available', 'effective_price')
        else:
            queryset = queryset.order_by('-is_available', '-effective_price')
    elif sort_option == 'pricedesc':
        queryset = queryset.order_by('-is_available', '-price')
    elif sort_option == 'popasc':
        queryset = queryset.order_by('-is_available', 'popularity')
    elif sort_option == 'popdesc':
        queryset = queryset.order_by('-is_available', '-popularity')
    elif sort_option == 'nameasc':
        queryset = queryset.order_by('-is_available', 'name', 'flavor')
    elif sort_option == 'namedesc':
        queryset = queryset.order_by('-is_available', '-name', 'flavor')
    else:
        queryset = queryset.order_by('-is_available', 'name', 'flavor')
    return queryset

def attach_review_data(queryset):
    review_counts = (
        Review.objects
        .values('item__fullname')
        .annotate(total_reviews=Count('id'), average_rating=Avg('rating'))
    )
    review_data = {r['item__fullname']: r for r in review_counts}
    unique_items = {}
    final_items = []

    for item in queryset:
        data = review_data.get(item.fullname, {'total_reviews': 0, 'average_rating': None})
        if item.fullname not in unique_items:
            unique_items[item.fullname] = item
            item.total_reviews = data['total_reviews']
            item.average_rating = data['average_rating']
            item.save()
            final_items.append(item)
        elif item.is_available:
            unique_items[item.fullname] = item

    return final_items

def build_query_from_params(request, fields):
    q_objects = Q()
    for field in fields:
        values = request.GET.getlist(field)
        if values:
            q_objects &= Q(**{f"{field}__in": values})
    return q_objects
