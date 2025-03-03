from django.db.models import F, Sum, Case, When, DecimalField

from supplement_store.models import Cart, Wishlist

def give_items(request):
    if request.user.is_authenticated:
        cart_items = (
            Cart.objects.filter(in_cart=True, user=request.user)
            .values('item__id', 'item__name', 'item__weight', 'item__price', 'item__sale_price', 'item__main_image', 'item__fullname', 'item__quantity', 'quantity')
            .annotate(total_quantity=Sum('quantity'),total_price=Sum(
                Case(
                    When(item__sale_price__isnull=False, then=F('item__sale_price')),
                    default=F('item__price'),
                    output_field=DecimalField(),
                    ) * F('quantity')
                )
            )
        )
        wishlist_items = (
            Wishlist.objects.filter(user=request.user)
        )
    else:
        cart_items = None
        wishlist_items = None
    return {
        "items_in_cart": cart_items,
        "items_in_wishlist": wishlist_items
    }