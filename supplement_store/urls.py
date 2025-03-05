from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views
from supplement_store.views import CustomPasswordResetView, CustomPasswordResetConfirmView

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login_view, name="login_view"),
    path('register', views.register_view, name="register_view"),
    path('logout', views.logout_view, name="logout_view"),
    path('account', views.account, name="account"),
    path('wishlist', views.wishlist, name="wishlist"),
    path('add_to_wishlist', views.add_to_wishlist, name="add_to_wishlist"),
    path('remove_wishlist', views.remove_wishlist, name="remove_wishlist"),
    path('remove_wishlist_all', views.remove_wishlist_all, name="remove_wishlist_all"),
    path('shopping_cart', views.shopping_cart, name="shopping_cart"),
    path('decrease_quantity/<int:id>', views.decrease_quantity, name="decrease_quantity"),
    path('increase_quantity/<int:id>', views.increase_quantity, name="increase_quantity"),
    path('remove_cart', views.remove_cart, name="remove_cart"),
    path('remove_cart_all', views.remove_cart_all, name="remove_cart_all"),
    path('delivery-and-payment', views.delivery_and_payment, name="delivery_and_payment"),
    path('summary', views.summary, name="summary"),
    path('create_new_order', views.create_new_order, name="create_new_order"),
    path('payment-done/', views.payment_done, name='payment_done'),
    path('payment-canceled/', views.payment_canceled, name='payment_canceled'),
    path('add_sale_to_item', views.add_sale_to_item, name="add_sale_to_item"),
    path('change_quantity_of_item', views.change_quantity_of_item, name="change_quantity_of_item"),
    path('add_item_to_shop', views.add_item_to_shop, name="add_item_to_shop"),
    path('add_item', views.add_item, name="add_item"),
    path('bulk_add_items', views.bulk_add_items, name="bulk_add_items"),
    path('newsletter', views.newsletter, name="newsletter"),
    path('send_email_to_newsletter', views.send_email_to_newsletter, name="send_email_to_newsletter"),
    path('brands', views.brands, name="brands"),
    path('about', views.about, name="about"),
    path('contact', views.contact, name="contact"),
    path('activate/<str:uidb64>/<str:token>/', views.activate_email, name="activate_email"),
    path('chatting', views.chatting, name="chatting"),
    path('load_messages', views.load_messages, name="load_messages"),
    path('inbox', views.inbox, name="inbox"),
    path('answer/<str:username>', views.answer_inbox, name="answer_inbox"),
    path('answering/<str:username>', views.answering, name="answering"),
    path('close/<str:username>', views.close, name="close"),

    path('clothing', views.clothing, name="clothing"),
    path('supplements', views.supplements, name="supplements"),
    path('brand/<str:brand>', views.shop_by_brand, name="shop_by_brand"),
    path('category/<str:category>', views.shop_by_category, name="shop_by_category"),
    path('<str:itemname>', views.shop_by_itemname, name="shop_by_itemname"),
    path('comment/<str:username>/<str:itemname>', views.comment, name="comment"),

    path('password_reset/', CustomPasswordResetView.as_view(
        template_name='supplement_store/password_reset_templates/password_reset_form.html', 
        email_template_name='supplement_store/password_reset_templates/password_reset_email.html', 
        subject_template_name='supplement_store/password_reset_templates/password_reset_subject.txt'), 
        name="password_reset"),
    path('password_reset/done', auth_views.PasswordResetDoneView.as_view(template_name='supplement_store/password_reset_templates/password_reset_done.html'), name="password_reset_done"),
    path('reset/<str:uidb64>/<str:token>', CustomPasswordResetConfirmView.as_view(template_name='supplement_store/password_reset_templates/password_reset_confirm.html'), name="password_reset_confirm"),
    path('reset/done', auth_views.PasswordResetCompleteView.as_view(template_name='supplement_store/password_reset_templates/password_reset_complete.html'), name="password_reset_complete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
