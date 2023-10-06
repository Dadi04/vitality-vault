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
    path('shopping_cart', views.shopping_cart, name="shopping_cart"),
    path('newsletter', views.newsletter, name="newsletter"),
    path('brands', views.brands, name="brands"),
    path('about', views.about, name="about"),
    path('contact', views.contact, name="contact"),
    path("activate/<str:uidb64>/<str:token>/", views.activate_email, name='activate_email'),
    path("chatting", views.chatting, name="chatting"),
    path('load_messages/', views.load_messages, name='load_messages'),
    path('inbox', views.inbox, name="inbox"),
    path('filter-products', views.filter_products, name='filter_products'),
    path('answer/<str:username>', views.answer_inbox, name="answer_inbox"),
    path('answering/<str:username>', views.answering, name="answering"),
    path('close/<str:username>', views.close, name="close"),


    path('supplements', views.supplements, name="supplements"),
    path('<str:brand>', views.shop_by_brand, name="shop_by_brand"),
    path('<str:brand>/<str:itemname>', views.shop_by_itemname, name="shop_by_itemname"),
    path('comment/<str:username>/<str:itemname>', views.comment, name="comment"),

    path('password_reset', CustomPasswordResetView.as_view(
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
