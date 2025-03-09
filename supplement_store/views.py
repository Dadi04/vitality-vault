from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.forms import SetPasswordForm
from django.http import JsonResponse
from django.db.models import Subquery, OuterRef, F, Avg, Sum, Q, Case, When, DecimalField, Window, Exists, BooleanField
from django.db.models.functions import RowNumber
from django.conf import settings
from django.core.paginator import Paginator

from paypal.standard.forms import PayPalPaymentsForm
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

from datetime import datetime
from decimal import Decimal

import pandas as pd

from .shop_utils import apply_sorting, attach_review_data, build_query_from_params, attach_image, merge_carts, merge_wishlists
from .forms import RegistrationForm, ItemForm, ShippingInformationForm
from .countries import COUNTRIES
from .models import User, SlideShowImage, Support, SupportAnswer, Item, Review, Cart, Wishlist, Transaction, TransactionItem, Newsletter

def index(request):
    return render(request, "supplement_store/index.html", {
        "images": SlideShowImage.objects.all().order_by('-order'),
    })

def about(request):
    return render(request, "supplement_store/about.html")

def brands(request):
    return render(request, "supplement_store/brands.html")

def contact(request):
    if request.method == 'POST':
        email_title = request.POST.get('email-title')
        email_body = request.POST.get('email-body')
        email_address = request.POST.get('email-address')
        email = EmailMessage(email_title, email_body, from_email=email_address ,to=['dadica.petkovic@gmail.com'])
        email.send()
    return render(request, "supplement_store/contact.html")

""" Account logic """
def login_view(request):
    if request.method == 'POST':
        first = request.POST.get('first')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        if '@' in first:
            user = User.objects.get(email=first)
        else:
            user = authenticate(request, username=first, password=password)

        if user is not None:
            if remember:
                user.remember_me = True
                user.save()
                request.session.set_expiry(1209600)
                request.session.modified = True
            else:
                user.remember_me = False
                user.save()
                request.session.set_expiry(0)
                request.session.modified = True
            
            login(request, user)
            merge_carts(request, user)
            merge_wishlists(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid login credentials. Please try again.", extra_tags="login_error")
            return redirect('login_view')
        
    return render(request, "supplement_store/login.html")

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            username = form.cleaned_data["username"]
            first = form.cleaned_data["first_name"]
            last = form.cleaned_data["last_name"]
            phone = form.cleaned_data["phone"]
            birthday = form.cleaned_data["birthday"]
            address = form.cleaned_data["address"]
            city = form.cleaned_data["city"]
            state = form.cleaned_data["state"]
            country = request.POST["country"]
            zipcode = form.cleaned_data["zipcode"]
            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]
            captcha = form.cleaned_data["captcha"]

            user = User.objects.create_user(username=username, email=email, password=password, first_name=first, last_name=last, phone=phone, birth=birthday, address=address, city=city, state=state, country=country, zipcode=zipcode)
            user.is_active = False
            user.save()

            mail_subject = "Activate your user account."
            message = render_to_string("supplement_store/confirmation_email.html", {
                "user": user.username,
                "domain": get_current_site(request).domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
                "protocol": 'https' if request.is_secure() else 'http'
            })
            email_message = EmailMessage(mail_subject, message, to=[email])
            email_message.send()

            return render(request, "supplement_store/loading.html")
    else:
        form = RegistrationForm()
    return render(request, "supplement_store/register.html", {
        "countries": [(code, name) for code, name in COUNTRIES.items()],
        "form": form
    })

def activate_email(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        
        login(request, user)
        merge_carts(request, user)
        merge_wishlists(request, user)
        return redirect('index')
    return redirect('register_view')

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def comment(request, username, itemname):
    if request.method == 'POST':
        item = Item.objects.filter(fullname=itemname).first()
        user = User.objects.get(username=username)
        comment = request.POST["textarea"]
        rating = request.POST["rating"]
        if comment and rating:
            Review.objects.create(user=user, item=item, comment=comment, rating=rating, timestamp=datetime.now())
            return redirect(request.META.get('HTTP_REFERER', 'index'))
        else:
            messages.error(request, 'Please provide a comment and a rating.', extra_tags="comment_error")
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def account(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, "supplement_store/account.html", {
        "transactions": transactions,
        "items": TransactionItem.objects.filter(transaction__in=transactions),
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = User.objects.get(username=request.user.username)
        user.email = request.POST.get('email', '')
        user.address = request.POST.get('address', '')
        user.city = request.POST.get('city', '')
        user.state = request.POST.get('state', '')
        user.country = request.POST.get('country', '')
        user.zipcode = request.POST.get('zipcode', '')
        user.phone = request.POST.get('phone', '')
        user.birth = request.POST.get('birth', '')
        user.save()

    return redirect('account')
""" End of Account logic """

""" Filtering logic """
def clothing(request):
    items = Item.objects.filter(size__isnull=False).order_by('name', '-is_available')
    unique_items = {}
    final_items = []

    for item in items:
        if item.fullname not in unique_items:
            unique_items[item.fullname] = item
            final_items.append(item) 
        elif item.is_available:
            unique_items[item.name] = item

    return render(request, "supplement_store/shop.html", {
        "items": final_items,
    })

def supplements(request):
    q_objects = build_query_from_params(request, ['category', 'subcategory', 'flavor', 'brand'])
    queryset = Item.objects.filter(q_objects)

    sort_option = request.GET.get('sort', 'nameasc')
    queryset = apply_sorting(queryset, sort_option)

    if request.user.is_authenticated:
        wishlist_qs = Wishlist.objects.filter(user=request.user, item=OuterRef('pk'))
        queryset = queryset.annotate(is_wishlisted=Exists(wishlist_qs))
    else: 
        wishlist_session = request.session.get("wishlist", [])
        queryset = queryset.annotate(is_wishlisted=Case(When(id__in=wishlist_session, then=True), default=False, output_field=BooleanField()))

    items = attach_review_data(queryset)

    paginator = Paginator(items, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    query_params = query_params.urlencode()

    return render(request, "supplement_store/shop.html", {
        "items": page_obj,
        "categories": Item.objects.filter().values_list('category', flat=True).distinct(),
        "subcategories": Item.objects.filter().values_list('subcategory', flat=True).distinct(),
        "flavors": Item.objects.filter().values_list('flavor', flat=True).distinct(),
        "brands": Item.objects.filter().values_list('brand', flat=True).distinct(),
        "current_sort": sort_option,
        "query_params": query_params,
    })

def shop_by_category(request, category):
    base_filter = Q(category=category)
    q_objects = build_query_from_params(request, ['category', 'subcategory', 'flavor', 'brand'])
    queryset = Item.objects.filter(base_filter & q_objects)

    sort_option = request.GET.get('sort', 'nameasc')
    queryset = apply_sorting(queryset, sort_option)

    if request.user.is_authenticated:
        wishlist_qs = Wishlist.objects.filter(user=request.user, item=OuterRef('pk'))
        queryset = queryset.annotate(is_wishlisted=Exists(wishlist_qs))
    else: 
        wishlist_session = request.session.get("wishlist", [])
        queryset = queryset.annotate(is_wishlisted=Case(When(id__in=wishlist_session, then=True), default=False, output_field=BooleanField()))

    items = attach_review_data(queryset)

    paginator = Paginator(items, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    query_params = query_params.urlencode()
 
    return render(request, "supplement_store/shop.html", {
        "items": page_obj,
        "categories": Item.objects.filter(category=category).values_list('category', flat=True).distinct(),
        "subcategories": Item.objects.filter(category=category).values_list('subcategory', flat=True).distinct(),
        "flavors": Item.objects.filter(category=category).values_list('flavor', flat=True).distinct(),
        "brands": Item.objects.filter(category=category).values_list('brand', flat=True).distinct(),
        "current_sort": sort_option,
        "query_params": query_params,
    })

def shop_by_brand(request, brand):
    base_filter = Q(brand=brand)
    q_objects = build_query_from_params(request, ['category', 'subcategory', 'flavor', 'brand'])
    queryset = Item.objects.filter(base_filter & q_objects)

    sort_option = request.GET.get('sort', 'nameasc')
    queryset = apply_sorting(queryset, sort_option)

    if request.user.is_authenticated:
        wishlist_qs = Wishlist.objects.filter(user=request.user, item=OuterRef('pk'))
        queryset = queryset.annotate(is_wishlisted=Exists(wishlist_qs))
    else: 
        wishlist_session = request.session.get("wishlist", [])
        queryset = queryset.annotate(is_wishlisted=Case(When(id__in=wishlist_session, then=True), default=False, output_field=BooleanField()))

    items = attach_review_data(queryset)

    paginator = Paginator(items, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    query_params = query_params.urlencode()

    return render(request, "supplement_store/shop.html", {
        "items": page_obj,
        "categories": Item.objects.filter(brand=brand).values_list('category', flat=True).distinct(),
        "subcategories": Item.objects.filter(brand=brand).values_list('subcategory', flat=True).distinct(),
        "flavors": Item.objects.filter(brand=brand).values_list('flavor', flat=True).distinct(),
        "brands": Item.objects.filter(brand=brand).values_list('brand', flat=True).distinct(),
        "current_sort": sort_option,
        "query_params": query_params,
    })

def shop_by_itemname(request, itemname):
    if request.user.is_authenticated:
        wishlist_qs = Wishlist.objects.filter(user=request.user, item=OuterRef('pk'))
        items = Item.objects.filter(fullname=itemname)\
            .annotate(
                row_number = Window(
                    expression=RowNumber(), 
                    partition_by=[F('flavor')], 
                    order_by=F('is_available').desc()
                ),
                is_wishlisted=Exists(wishlist_qs)
            )\
            .filter(row_number = 1)\
            .order_by('-is_available')
    else: 
        wishlist_session = request.session.get("wishlist", [])
        items = Item.objects.filter(fullname=itemname)\
            .annotate(
                row_number=Window(
                    expression=RowNumber(), 
                    partition_by=[F('flavor')], 
                    order_by=F('is_available').desc()
                ),
                is_wishlisted=Case(
                    When(id__in=wishlist_session, then=True),
                    default=False,
                    output_field=BooleanField()
                )
            )\
            .filter(row_number=1)\
            .order_by('-is_available')
    
    if not items.exists():
        return render(request, "supplement_store/error.html")

    flavor_option = request.GET.get('flavor')
    if not flavor_option:
        first_item = items.first()
        if first_item:
            flavor_option = first_item.flavor

    if request.user.is_authenticated:
        wishlist_qs = Wishlist.objects.filter(user=request.user, item=OuterRef('pk'))
        item_chosen = Item.objects.filter(fullname=itemname, flavor=flavor_option)\
            .annotate(is_wishlisted=Exists(wishlist_qs))\
            .first()
    else:
        session_wishlist_ids = request.session.get("wishlist", [])
        item_chosen = Item.objects.filter(fullname=itemname, flavor=flavor_option)\
            .annotate(
                is_wishlisted=Case(
                    When(id__in=session_wishlist_ids, then=True),
                    default=False,
                    output_field=BooleanField()
                )
            )\
            .first()

    if items:
        subcategory = items.first().subcategory
        similar_items = Item.objects.filter(subcategory=subcategory).distinct('fullname')

        items_fullnames = set(item.fullname for item in items)
        similar_items = [item for item in similar_items if item.fullname not in items_fullnames]
    else:
        similar_items = None

    all_reviews = Review.objects.filter(item=Item.objects.filter(fullname=itemname).first()).order_by('-timestamp')
    try:
        count = int(request.GET.get('count', 5))
    except ValueError:
        count = 5
    reviews = all_reviews[:count]

    average_review = all_reviews.aggregate(Avg('rating'))['rating__avg']

    return render(request, "supplement_store/item.html", {
        "item_chosen": item_chosen,
        "items": items,
        "reviews": reviews,
        "average_review": average_review,
        "similar_items": similar_items,
        "count": count,
        "total_reviews": all_reviews.count(),
    })

def search_items(request):
    query = request.GET.get('q', '')
    if query:
        items = list(
            Item.objects.filter(
                Q(name__icontains=query) |
                Q(brand__icontains=query) |
                Q(category__icontains=query)
            ).order_by('-popularity')[:5].values('id', 'fullname', 'name', 'brand', 'flavor', 'price', 'main_image')
        )
    else:
        items = []
    return JsonResponse({'items': items})
    
""" End of filtering logic """

""" Wishlist """
def wishlist(request):
    if request.user.is_authenticated:
        items = Wishlist.objects.filter(user=request.user)
    else:
        wishlist_ids = request.session.get("wishlist", [])
        items = []
        for item_id in wishlist_ids:
            try:
                item = Item.objects.get(id=item_id)
                wishlist_item = Wishlist(item=item)
                items.append(wishlist_item)
            except Item.DoesNotExist:
                continue
    return render(request, "supplement_store/wishlist.html", {
        "items": items,
    })

def add_to_wishlist(request):
    if request.method == 'POST':
        item_id = request.POST.get('id')
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return redirect(request.META.get('HTTP_REFERER', 'index')) 

        if request.user.is_authenticated:
            Wishlist.objects.create(user=request.user, item=item)
        else:
            wishlist_session = request.session.get("wishlist", [])
            if item_id not in wishlist_session:
                wishlist_session.append(item_id)
                request.session["wishlist"] = wishlist_session
    return redirect(request.META.get('HTTP_REFERER', 'index')) 

def remove_wishlist(request):
    if request.method == 'POST':
        item_id = request.POST.get("item_id")
        if request.user.is_authenticated:
            try:
                item = Item.objects.get(id=item_id)
                Wishlist.objects.filter(user=request.user, item=item).delete()
            except Item.DoesNotExist:
                pass
        else:
            wishlist_session = request.session.get("wishlist", [])
            if item_id in wishlist_session:
                wishlist_session.remove(item_id)
                request.session["wishlist"] = wishlist_session        
    return redirect(request.META.get('HTTP_REFERER', 'index')) 

def remove_wishlist_all(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            Wishlist.objects.filter(user=request.user).delete()
        else:
            del request.session["wishlist"]
    return redirect(request.META.get('HTTP_REFERER', 'index')) 
""" End of Wishlist """

""" Shopping Cart """
def shopping_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get("id")
        item = Item.objects.get(id=item_id)
        try:
            quantity = int(request.POST.get("quantity"))
        except (ValueError, TypeError):
            quantity = 1
        if not item.is_available:
            return redirect(request.META.get('HTTP_REFERER', 'index'))
        if quantity > item.quantity:
            return redirect('shop_by_itemname', fullname=item.fullname)
        
        if request.user.is_authenticated:
            Cart.objects.create(user=request.user, item=item, quantity=quantity, in_cart=True)
        else:
            cart = request.session.get("cart", {})
            key = str(item_id)
            cart[key] = cart.get(key, 0) + quantity
            request.session["cart"] = cart

        return redirect(request.META.get('HTTP_REFERER', 'index'))       
    
    if request.user.is_authenticated:
        cart_items = (
            Cart.objects.filter(in_cart=True, user=request.user)
            .values('item__id', 'item__name', 'item__weight', 'item__price', 'item__sale_price', 'item__main_image', 'item__fullname', 'item__quantity')
            .annotate(total_quantity=Sum('quantity'), total_price=Sum(
                Case(
                    When(item__sale_price__isnull=False, then=F('item__sale_price')),
                        default=F('item__price'),
                        output_field=DecimalField(),
                    ) * F('quantity')
                )
            )
        )
        context = {"items": cart_items}
    else:
        session_cart = request.session.get("cart", {})
        cart_items = []
        for id_str, qty in session_cart.items():
            try:
                item = Item.objects.get(id=id_str)
                total_price = (item.sale_price if item.sale_price is not None else item.price) * qty
                cart_items.append({
                    "item__id": item.id,
                    "item__name": item.name,
                    "item__weight": item.weight,
                    "item__price": item.price,
                    "item__sale_price": item.sale_price,
                    "item__main_image": item.main_image.url if item.main_image else None,
                    "item__fullname": item.fullname,
                    "item__quantity": item.quantity,
                    "total_quantity": qty,
                    "total_price": total_price,
                })
            except Item.DoesNotExist:
                continue
        context = {"items": cart_items}
    return render(request, "supplement_store/cart.html", context)
    
def remove_cart(request):
    if request.method == 'POST':  
        item_id = request.POST.get("item_id")
        if request.user.is_authenticated:
            try:
                item = Item.objects.get(id=item_id)
                Cart.objects.filter(item=item, user=request.user, in_cart=True).delete()
            except Item.DoesNotExist:
                pass
        else:
            session_cart = request.session.get("cart", {})
            if item_id in session_cart:
                del session_cart[item_id]
                request.session["cart"] = session_cart

    return redirect(request.META.get('HTTP_REFERER', 'index'))

def remove_cart_all(request):
    if request.method == 'POST': 
        if request.user.is_authenticated:
            Cart.objects.filter(user=request.user, in_cart=True).delete()
        else:
            del request.session["cart"]
    return redirect(request.META.get('HTTP_REFERER', 'index'))

def decrease_quantity(request, id):
    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(item__id=id, user=request.user).first()
        if cart_item and cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
    else:
        session_cart = request.session.get("cart", {})
        item_key = str(id)
        if item_key in session_cart:
            if session_cart[item_key] > 1:
                session_cart[item_key] -= 1
            else:
                del session_cart[item_key]
            request.session["cart"] = session_cart
    return redirect(request.META.get('HTTP_REFERER', 'index'))

def increase_quantity(request, id):
    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(item__id=id, user=request.user).first()
        if cart_item and cart_item.quantity < cart_item.item.quantity:
            cart_item.quantity += 1
            cart_item.save()
    else:
        session_cart = request.session.get("cart", {})
        item_key = str(id)
        try:
            item = Item.objects.get(id=id)
        except Item.DoesNotExist:
            return redirect(request.META.get('HTTP_REFERER', 'index'))
        current_qty = session_cart.get(item_key, 0)
        if current_qty < item.quantity:
            session_cart[item_key] = current_qty + 1
            request.session["cart"] = session_cart

    return redirect(request.META.get('HTTP_REFERER', 'index'))
""" End of Shopping Cart """

""" Purchase System """
@login_required
def delivery_and_payment(request):
    items = Cart.objects.filter(user=request.user, in_cart=True)
    if not items:
        return redirect('shopping_cart')
    shipping_info = request.session.get('shipping_info', {})
    form = ShippingInformationForm(initial=shipping_info)

    return render(request, "supplement_store/delivery_payment.html", {"form": form})

@login_required
def summary(request):
    items = Cart.objects.filter(user=request.user, in_cart=True)
    if not items:
        return redirect('shopping_cart')
    
    if request.method == 'POST':
        form = ShippingInformationForm(request.POST)
        if form.is_valid():
            request.session['shipping_info'] = form.cleaned_data
    else:
        initial_data = request.session.get('shipping_info', {})
        form = ShippingInformationForm(initial=initial_data)

    shipping_info = request.session.get('shipping_info')    
    return render(request, "supplement_store/summary.html", {
        "email": shipping_info.get("email"),
        "name": shipping_info.get("first_name"),
        "surname": shipping_info.get("last_name"),
        "address": shipping_info.get("address"),
        "city": shipping_info.get("city"),
        "state": shipping_info.get("state", ""),
        "country": shipping_info.get("country"),
        "zipcode": shipping_info.get("zipcode"),
        "phone": shipping_info.get("phone"),
        "payment_method": shipping_info.get("payment_method"),
        "items": items,
    })

@login_required
def create_new_order(request):
    items_in_cart = Cart.objects.filter(user=request.user, in_cart=True)
    shipping_info = request.session.get('shipping_info')
    if not items_in_cart:
        return redirect('shopping_cart')
    
    transaction = Transaction.objects.create(user=request.user, date=datetime.now(), status='pending')
    total_price = Decimal('0.00')

    for cart_item in items_in_cart:
        item = cart_item.item
        quantity = cart_item.quantity

        TransactionItem.objects.create(transaction=transaction, item=item, quantity=quantity)
        total_price += item.price * quantity
    
    transaction.total_price = total_price
    transaction.email = shipping_info.get("email")
    transaction.first_name = shipping_info.get("first_name")
    transaction.last_name = shipping_info.get("last_name")
    transaction.phone = shipping_info.get("phone")
    transaction.address = shipping_info.get("address")
    transaction.city = shipping_info.get("city")
    transaction.zipcode = shipping_info.get("zipcode")
    transaction.state = shipping_info.get("state", "")
    transaction.country = shipping_info.get("country")
    transaction.save()

    payment_method = shipping_info.get("payment_method", "").lower()
    request.session['transaction_id'] = transaction.id
    if payment_method == 'paypal':
        host = request.get_host()

        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': '%.2f' % transaction.total_price,
            'item_name': f'Order {transaction.id}',
            'invoice': str(transaction.id),
            'currency_code': 'USD',
            'notify_url': f'http://{host}{reverse("paypal-ipn")}',
            'return_url': f'http://{host}{reverse("payment_done")}',
            'cancel_return': f'http://{host}{reverse("payment_canceled")}',
        }

        form = PayPalPaymentsForm(initial=paypal_dict)
        return render(request, 'supplement_store/process_payment.html', {
            'form': form,
            'transaction': transaction,
        })
    elif payment_method == 'stripe':
        domain = request.build_absolute_uri('/')[:-1]
        line_items = []
        for cart_item in items_in_cart:
            unit_amount = int(cart_item.item.price * 100)
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': unit_amount,
                    'product_data': {
                        'name': cart_item.item.name,
                    },
                },
                'quantity': cart_item.quantity,
            })
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=domain + reverse('payment_done') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain + reverse('payment_canceled'),
            )
        except Exception as e:
            print(e)
            return redirect('index')
        return redirect(session.url, code=303)
    else:
        return redirect('index')

@login_required
def payment_done(request):
    transaction_id = request.session.get('transaction_id')
    if not transaction_id:
        return redirect('shopping_cart')
    transaction = get_object_or_404(Transaction, id=transaction_id)
    transaction.status = 'paid'
    transaction.save()

    item_list = []
    for t_item in transaction.transactionitem_set.all():
        item = t_item.item
        item.quantity -= t_item.quantity
        if item.quantity == 0:
            item.is_available = False
        item.popularity += 1
        item.save()
        item_list.append(f'{t_item.item.name} (x{t_item.quantity}) - ${t_item.item.price * t_item.quantity}')

    item_detail = '\n'.join(item_list)
    mail_subject = "New Order Just Arrived"
    message = (
        f"Dear {request.user.username},\n\n"
        f"Your order (Transaction ID: {transaction.id}) has been confirmed.\n"
        f"Total Price: ${transaction.total_price}\n\n"
        f"Items ordered:\n{item_detail}\n\n"
        "Thank you for shopping with us!"
    )

    email = EmailMessage(mail_subject, message, to=['dadica.petkovic@gmail.com', request.user.email])
    email.send()

    Cart.objects.filter(user=request.user, in_cart=True).delete()

    request.session.pop('shipping_info', None)
    request.session.pop('transaction_id', None)

    return render(request, 'supplement_store/payment_done.html')

@login_required
def payment_canceled(request):
    transaction_id = request.session.get('transaction_id')
    if transaction_id:
        transaction = get_object_or_404(Transaction, id=transaction_id)
        transaction.status = 'canceled'
        transaction.save()

        request.session.pop('shipping_info', None)
        request.session.pop('transaction_id', None)
        
    return render(request, 'supplement_store/payment_canceled.html')
""" End of Purchase System """

""" Admin/support tools """
def newsletter(request):
    email = request.POST.get('email')
    if email:
        newsletter_exist = Newsletter.objects.filter(email=email)
        if not newsletter_exist:
            Newsletter.objects.create(email=email)
        else:
            messages.error(request, 'Email is already registered for newslatter.', extra_tags="newsletter_error")
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def send_email_to_newsletter(request):
    if request.method == 'POST':
        emails = Newsletter.objects.all()
        email_title = request.POST.get('email-title')
        email_body = request.POST.get('email-body')

        for email_address in emails:
            email = EmailMessage(email_title, email_body, to=[email_address.email])
            email.send()

    return render(request, "supplement_store/newsletter.html")

@login_required
def add_sale_to_item(request):
    if request.user.is_staff or request.user.is_support:
        if request.method == 'POST':
            ids = request.POST.getlist('id')
            sale_prices = request.POST.getlist('sale-price')
            start_dates = request.POST.getlist('sale-date-start')
            end_dates = request.POST.getlist('sale-date-end')
            sale_data = list(zip(ids, sale_prices, start_dates, end_dates))
            user_sale_items = {}
            for id, price, start, end in sale_data:
                if price:
                    try:
                        item = Item.objects.get(id=id)
                    except item.DoesNotExist:
                        continue
                    item.sale_price = price
                    item.sale_start_date = start
                    item.sale_end_date = end
                    item.save()
                    wishlists = Wishlist.objects.filter(item=item)
                    for wishlist in wishlists:
                        user_email = wishlist.user.email
                        user_sale_items.setdefault(user_email, []).append(item)
            print(user_sale_items)
            for email, sale_items in user_sale_items.items():
                subject = f"{len(sale_items)} items from your wishlist are on sale"
                body_lines = []
                for sale_item in sale_items:
                    line = f"{sale_item.fullname} Flavor: {sale_item.flavor} - Sale Price: {sale_item.sale_price}"
                    body_lines.append(line)
                body = "\n".join(body_lines)
                email_message = EmailMessage(subject, body, to=[email])
                email_message.send()
        return render(request, "supplement_store/add_sale_to_item.html", {
            "items": Item.objects.all().order_by('id'),
        })

    return redirect('index')

@login_required
def change_quantity_of_item(request):
    if request.user.is_staff or request.user.is_support:
        if request.method == 'POST':
            ids = request.POST.getlist('id')
            quantities = request.POST.getlist('quantity')
            quantity_data = list(zip(ids, quantities))
            for id, quantity in quantity_data:
                if quantity:
                    item = Item.objects.get(id=id)
                    item.quantity = quantity
                    item.save()
        return render(request, "supplement_store/change_quantity_of_item.html", {
            "items": Item.objects.all().order_by('id'),
        })
    return redirect('index')

@login_required
def add_item_to_shop(request):
    if request.user.is_staff or request.user.is_support:
        return render(request, "supplement_store/add_item_to_shop.html")
    return redirect('index')

@login_required
def add_item(request):
    if not (request.user.is_staff or request.user.is_support):
        return redirect('index')
    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_item_to_shop')
    else:
        form = ItemForm()

    return render(request, "supplement_store/add_item_to_shop.html")     

@login_required
def bulk_add_items(request):
    if not (request.user.is_staff or request.user.is_support):
        return redirect('index')

    if request.method == 'POST' and request.FILES.get('items_file'):
        file = request.FILES.get('items_file')
        df = pd.read_excel(file)

        for _, row in df.iterrows():
            sale_price = row['Sale Price'] if pd.notnull(row['Sale Price']) else None
            sale_start_date = row['Sale Start Date'] if pd.notnull(row['Sale Start Date']) else None
            sale_end_date = row['Sale End Date'] if pd.notnull(row['Sale End Date']) else None

            existing_item = Item.objects.filter(fullname=row['Fullname'], flavor=row['Flavor']).first()
            if existing_item:
                additional_quantity = row['Quantity'] if pd.notnull(row['Quantity']) else 0
                existing_item.quantity += additional_quantity
                existing_item.save()
            else:
                item = Item(
                    name = row['Name'],
                    fullname = row['Fullname'],
                    category = row['Category'],
                    subcategory = row['Subcategory'],
                    description = row['Description'],
                    brand = row['Brand'],
                    price = row['Price'],
                    is_available = row['Is Available?'],
                    quantity = row['Quantity'],
                    sale_price = sale_price,
                    sale_start_date = sale_start_date,
                    sale_end_date = sale_end_date,
                    weight = row['Weight'],
                    flavor = row['Flavor'],
                    gender = row['Gender'],
                    size = row['Size'],
                    color = row['Color'],
                    is_new = row['Is New?'],
                    popularity = row['Popularity']
                )
                item.save()

                attach_image(item.main_image, row['Main Image'])
                attach_image(item.image1, row['Image1'])
                attach_image(item.image2, row['Image2'])
                attach_image(item.image3, row['Image3'])

                item.save()
    return render(request, "supplement_store/add_item_to_shop.html")
""" End of admin/support tools """

""" Messaging system """
@login_required
def chatting(request):
    if request.method == 'POST':
        message = request.POST.get('text-field', '')
        if message:
            Support.objects.create(user=request.user, message=message, date=datetime.now())
            return JsonResponse({'success': 'Message saved to the database'})
        else:
            return JsonResponse({'error': 'Message is empty'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def inbox(request):
    if request.user.is_staff or request.user.is_support:
        latest_message_subquery = Support.objects.filter(user=OuterRef('user')).order_by('-date').values('message')[:1]
        one_message_per_user = Support.objects.annotate(latest_message=Subquery(latest_message_subquery)).filter(message=F('latest_message'), is_closed=False)
        messages = one_message_per_user.all()
        return render(request, "supplement_store/inbox.html", {
            "messages": messages
        })
    return redirect('index')

@login_required
def answer_inbox(request, username):
    if request.user.is_staff or request.user.is_support:
        user = User.objects.get(username=username)
        support_messages = Support.objects.filter(user=user, is_closed=False)
        answer_messages = SupportAnswer.objects.filter(latest_message__in=support_messages, latest_message__is_closed=False)

        combined_messages = list(support_messages) + list(answer_messages)
        sorted_messages = sorted(combined_messages, key=lambda x: x.date, reverse=True)

        return render(request, "supplement_store/answer_inbox.html", {
            "messages": sorted_messages,
            "username": username
        })
    return redirect('index')

@login_required
def close(request, username):
    if request.user.is_staff or request.user.is_support:
        user = User.objects.get(username=username)
        all_support_messages = Support.objects.filter(user=user)
        for support in all_support_messages:
            support.is_closed = True
            support.save()
        all_answer_messages = SupportAnswer.objects.filter(latest_message__in=all_support_messages)
        for answer in all_answer_messages:
            answer.latest_message.is_closed = True
            answer.save()
    return redirect('index')

@login_required
def answering(request, username):
    if request.user.is_staff or request.user.is_support:
        user = User.objects.get(username=username)
        latest_message = Support.objects.filter(user=user, is_closed=False).order_by('-date').first()
        response = request.POST["text"]
        SupportAnswer.objects.create(
            response=response, 
            latest_message=latest_message, 
            date=datetime.now(), 
            answered_by=User.objects.get(username=request.user.username))
        latest_message.is_answered = True
        latest_message.save()
        return redirect('answer_inbox', username=user.username)
    return redirect('index')    

@login_required
def load_messages(request):
    if request.method == 'GET':
        support_messages = Support.objects.filter(user=request.user, is_closed=False)
        support_answer_messages = SupportAnswer.objects.filter(latest_message__user=request.user, latest_message__is_closed=False)
        messages = []

        combined_messages = list(support_messages) + list(support_answer_messages)
        sorted_messages = sorted(combined_messages, key=lambda x: x.date, reverse=False)

        for message in sorted_messages:
            if isinstance(message, Support):
                messages.append({
                    'type': 'support',
                    'message': message.message,
                    'sender': message.user.username,
                })
            elif isinstance(message, SupportAnswer):
                messages.append({
                    'type': 'support_answer',
                    'message': message.response,
                    'receiver': message.answered_by.username,
                })

        return JsonResponse({'messages': messages})
    return JsonResponse({'error': 'Invalid request method'}, status=400)
""" End of messaging system """

class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            form.add_error('email', 'Email does not exist.')
            return self.form_invalid(form)
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('password_reset_done')
    
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = SetPasswordForm

    def form_valid(self, form):
        password1 = form.cleaned_data['new_password1']
        password2 = form.cleaned_data['new_password2']

        if password1 != password2:
            form.add_error('new_password2', 'Passwords do not match')
            return self.form_invalid(form)

        response = super().form_valid(form)

        update_session_auth_hash(self.request, self.request.user)

        return response