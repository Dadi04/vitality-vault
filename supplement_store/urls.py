from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login, name="login"),
    path('register', views.register, name="register"),
    path('logout', views.logout, name="logout"),
    path('reset_password', views.reset_password, name="reset_password"),
    path('account', views.account, name="account"),
    path('wishlist', views.wishlist, name="wishlist"),
    path('shopping_cart', views.shopping_cart, name="shopping_cart"),
    path('newsletter', views.newsletter, name="newsletter"),
    path('brands', views.brands, name="brands"),
    path('about', views.about, name="about"),
    path('contact', views.contact, name="contact"),
]