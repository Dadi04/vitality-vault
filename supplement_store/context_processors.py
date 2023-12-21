from django.shortcuts import render
from django.db.models import F, Sum

from supplement_store.models import Cart

def give_items_in_cart(request):
    cart_items = (
        Cart.objects.filter(in_cart=True, user=request.user).values('item__id', 'item__name', 'item__weight', 'item__price', 'item__main_image', 'item__fullname', 'item__quantity')
        .annotate(total_quantity=Sum('quantity'),total_price=Sum(F('item__price') * F('quantity')))
    )
    return {"items_in_cart": cart_items,}