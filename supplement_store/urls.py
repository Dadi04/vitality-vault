from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login_view, name="login_view"),
    path('register', views.register_view, name="register_view"),
    path('logout', views.logout_view, name="logout_view"),
    path('reset_password', views.reset_password, name="reset_password"),
    path('account', views.account, name="account"),
    path('wishlist', views.wishlist, name="wishlist"),
    path('shopping_cart', views.shopping_cart, name="shopping_cart"),
    path('newsletter', views.newsletter, name="newsletter"),
    path('brands', views.brands, name="brands"),
    path('about', views.about, name="about"),
    path('contact', views.contact, name="contact"),
    path("activate/<str:uidb64>/<str:token>/", views.activate_email, name='activate_email'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
