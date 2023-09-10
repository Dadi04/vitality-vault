from django.shortcuts import render

from .models import User

# Create your views here.

def index(request):
    return render(request, "supplement_store/index.html")

def login(request):
    return render(request, "supplement_store/login.html")

def register(request):
    return render(request, "supplement_store/register.html")

def logout(request):
    return render(request, "supplement_store/index.html")

def account(request):
    return render(request, "supplement_store/account.html")

def wishlist(request):
    return render(request, "supplement_store/wishlist.html")

def shopping_cart(request):
    return render(request, "supplement_store/cart.html")