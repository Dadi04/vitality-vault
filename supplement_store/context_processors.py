from django.db.models import F, Sum, Case, When, DecimalField

from supplement_store.models import Cart, Wishlist, Item

from .countries import COUNTRIES

def give_items(request):
    if request.user.is_authenticated:
        cart_items = (
            Cart.objects.filter(in_cart=True, user=request.user)
            .values('item__id', 'item__name', 'item__weight', 'item__price', 'item__sale_price', 'item__main_image', 'item__fullname', 'item__quantity', 'quantity')
            .annotate(
                total_quantity=Sum('quantity'),
                total_price=Sum(
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
        session_cart = request.session.get("cart", {})
        cart_items = []
        for item_id_str, quantity in session_cart.items():
            try:
                item = Item.objects.get(id=item_id_str)
            except Item.DoesNotExist:
                continue
            unit_price = item.sale_price if item.sale_price is not None else item.price
            total_price = unit_price * quantity
            cart_items.append({
                "item__id": item.id,
                "item__name": item.name,
                "item__weight": item.weight,
                "item__price": item.price,
                "item__sale_price": item.sale_price,
                "item__main_image": item.main_image.url if item.main_image else None,
                "item__fullname": item.fullname,
                "item__quantity": item.quantity,
                "quantity": quantity,
                "total_quantity": quantity,
                "total_price": total_price,
            })
        wishlist_session = request.session.get("wishlist", [])
        wishlist_items = Item.objects.filter(id__in=wishlist_session)    
    return {
        "brands_list": Item.BRANDS,
        "categories_list": Item.CATEGORIES,
        "countries_list": COUNTRIES.items(),
        "items_in_cart": cart_items,
        "items_in_wishlist": wishlist_items
    }