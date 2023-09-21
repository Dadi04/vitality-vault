from django.contrib import admin

from .models import User, Item, InStock, Review, Cart, Wishlist, Transaction, Coupon, SlideShowImage

# Register your models here.

admin.site.register(User)
admin.site.register(Item)
admin.site.register(InStock)
admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(Transaction)
admin.site.register(Coupon)
admin.site.register(SlideShowImage)