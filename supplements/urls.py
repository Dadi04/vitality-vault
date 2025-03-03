"""
URL configuration for supplements project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from supplement_store import views

urlpatterns = [
    path('accounts/3rdparty/login/cancelled/', views.login_view, name='socialaccount_login_cancelled'),
    path('accounts/login/', views.login_view, name='account_login'),
    path('accounts/signup/', views.register_view, name='account_signup'),
    path('', include('supplement_store.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('paypal/', include('paypal.standard.ipn.urls')),
]
