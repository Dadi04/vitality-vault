from django.contrib import admin

from .models import User, Item, Review, Cart, Wishlist, SlideShowImage, Support, SupportAnswer, Transaction, TransactionItem, Newsletter

# Register your models here.

admin.site.register(User)
admin.site.register(Item)
admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(Transaction)
admin.site.register(TransactionItem)
admin.site.register(SlideShowImage)
admin.site.register(Support)
admin.site.register(SupportAnswer)
admin.site.register(Newsletter)