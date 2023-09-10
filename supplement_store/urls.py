from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login, name="login"),
    path('register', views.register, name="register"),
    path('logout', views.logout, name="logout"),
    path('account', views.account, name="account"),
    path('wishlist', views.wishlist, name="wishlist"),
    path('shopping_cart', views.shopping_cart, name="shopping_cart"),
]