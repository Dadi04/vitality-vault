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
from django.db.models import Subquery, OuterRef, F, Avg, Sum, Q, Case, When, DecimalField, Window, Exists
from django.db.models.functions import RowNumber
from django.conf import settings
from django.core.files import File

from paypal.standard.forms import PayPalPaymentsForm

from datetime import datetime
from decimal import Decimal

import os
import pandas as pd

from .shop_utils import apply_sorting, attach_review_data, build_query_from_params
from .forms import RegistrationForm, ItemForm, ShippingInformationForm
from .countries import COUNTRIES
from .models import User, SlideShowImage, Support, SupportAnswer, Item, Review, Cart, Wishlist, Transaction, TransactionItem

# Create your views here.

def index(request):
    return render(request, "supplement_store/index.html", {
        "images": SlideShowImage.objects.all().order_by('-order'),
    })

def login_view(request):
    if request.method == 'POST':
        first = request.POST.get("first")
        password = request.POST.get("password")
        remember = request.POST.get("remember")

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
            return redirect('index')
        else:
            messages.error(request, "Invalid login credentials. Please try again.")
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
            email = EmailMessage(mail_subject, message, to=[email])
            email.send()

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
        return redirect('index')
    return redirect('register_view')

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

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

    wishlist_qs = Wishlist.objects.filter(user=request.user, item=OuterRef('pk'))
    queryset = queryset.annotate(is_wishlisted=Exists(wishlist_qs))

    items = attach_review_data(queryset)

    return render(request, "supplement_store/shop.html", {
        "items": items,
        "categories": Item.objects.filter().values_list('category', flat=True).distinct(),
        "subcategories": Item.objects.filter().values_list('subcategory', flat=True).distinct(),
        "flavors": Item.objects.filter().values_list('flavor', flat=True).distinct(),
        "brands": Item.objects.filter().values_list('brand', flat=True).distinct()
    })

def shop_by_category(request, category):
    base_filter = Q(category=category)
    q_objects = build_query_from_params(request, ['category', 'subcategory', 'flavor', 'brand'])
    queryset = Item.objects.filter(base_filter & q_objects)

    sort_option = request.GET.get('sort', 'nameasc')
    queryset = apply_sorting(queryset, sort_option)

    wishlist_qs = Wishlist.objects.filter(user=request.user, item=OuterRef('pk'))
    queryset = queryset.annotate(is_wishlisted=Exists(wishlist_qs))

    items = attach_review_data(queryset)
 
    return render(request, "supplement_store/shop.html", {
        "items": items,
        "categories": Item.objects.filter(category=category).values_list('category', flat=True).distinct(),
        "subcategories": Item.objects.filter(category=category).values_list('subcategory', flat=True).distinct(),
        "flavors": Item.objects.filter(category=category).values_list('flavor', flat=True).distinct(),
        "brands": Item.objects.filter(category=category).values_list('brand', flat=True).distinct()
    })

def shop_by_brand(request, brand):
    base_filter = Q(brand=brand)
    q_objects = build_query_from_params(request, ['category', 'subcategory', 'flavor', 'brand'])
    queryset = Item.objects.filter(base_filter & q_objects)

    sort_option = request.GET.get('sort', 'nameasc')
    queryset = apply_sorting(queryset, sort_option)

    wishlist_qs = Wishlist.objects.filter(user=request.user, item=OuterRef('pk'))
    queryset = queryset.annotate(is_wishlisted=Exists(wishlist_qs))

    items = attach_review_data(queryset)

    return render(request, "supplement_store/shop.html", {
        "items": items,
        "categories": Item.objects.filter(brand=brand).values_list('category', flat=True).distinct(),
        "subcategories": Item.objects.filter(brand=brand).values_list('subcategory', flat=True).distinct(),
        "flavors": Item.objects.filter(brand=brand).values_list('flavor', flat=True).distinct(),
        "brands": Item.objects.filter(brand=brand).values_list('brand', flat=True).distinct()
    })

def shop_by_itemname(request, itemname):
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
    
    if not items.exists():
        return render(request, "supplement_store/error.html")

    flavor_option = request.GET.get('flavor')
    if not flavor_option:
        first_item = items.first()
        if first_item:
            flavor_option = first_item.flavor

    item_chosen = Item.objects.filter(fullname=itemname, flavor=flavor_option)\
        .annotate(is_wishlisted=Exists(wishlist_qs))\
        .first()

    if items:
        for item in items:
            subcategory = item.subcategory
        similar_items = Item.objects.filter(subcategory=subcategory).distinct('fullname')

        items_fullnames = set(item.fullname for item in items)
        similar_items = [item for item in similar_items if item.fullname not in items_fullnames]
    else:
        similar_items = None
    reviews = Review.objects.filter(item=Item.objects.filter(fullname=itemname).first()).order_by('-timestamp')
    average_review = reviews.aggregate(Avg('rating'))['rating__avg']

    return render(request, "supplement_store/item.html", {
        "item_chosen": item_chosen,
        "items": items,
        "reviews": reviews,
        "average_review": average_review,
        "similar_items": similar_items,
    })

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
            messages.error(request, 'Please provide a comment and a rating.')
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def account(request):
    return render(request, "supplement_store/account.html")

def reset_password(request):
    return render(request, "supplement_store/reset_password.html")

@login_required
def wishlist(request):
    return render(request, "supplement_store/wishlist.html", {
        "items": Wishlist.objects.filter(user=request.user),
    })

@login_required
def add_to_wishlist(request):
    if request.method == 'POST':
        item = Item.objects.get(id=request.POST.get("id"))
        Wishlist.objects.create(user=request.user, item=item)
    return redirect(request.META.get('HTTP_REFERER', 'index')) 
# staviti da ukoliko je vec wishlistovao da ne moze da se wishlistuje opet u shopu i u items

@login_required
def remove_wishlist(request):
    if request.method == 'POST':
        item = Item.objects.get(id=request.POST.get("item_id"))
        Wishlist.objects.filter(user=request.user, item=item).delete()
    return redirect(request.META.get('HTTP_REFERER', 'index')) 

@login_required
def remove_wishlist_all(request):
    if request.method == 'POST':
        Wishlist.objects.filter(user=request.user).delete()
    return redirect(request.META.get('HTTP_REFERER', 'index')) 

@login_required
def process_payment(request):
    transaction_id = request.session.get('transaction_id')
    if not transaction_id:
        return redirect('shopping_cart')
    transaction = get_object_or_404(Transaction, id=transaction_id)
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

@login_required
def payment_done(request):
    request.session.pop('transaction_id', None)
    return render(request, 'supplement_store/payment_done.html')

@login_required
def payment_canceled(request):
    request.session.pop('transaction_id', None)
    return render(request, 'supplement_store/payment_canceled.html')

@login_required
def create_new_order(request):
    items_in_cart = Cart.objects.filter(user=request.user, in_cart=True)
    if not items_in_cart:
        return redirect('shopping_cart')
    
    transaction = Transaction.objects.create(user=request.user, date=datetime.now())

    total_price = Decimal('0.00')
    item_list = []

    for cart_item in items_in_cart:
        item = cart_item.item
        quantity = cart_item.quantity

        TransactionItem.objects.create(transaction=transaction, item=item, quantity=quantity)
        total_price += item.price * quantity

        item_list.append(f'{item.name} (x{quantity}) - ${item.price * quantity}')

        Item.objects.filter(id=item.id).update(quantity=item.quantity - quantity, popularity=item.popularity + 1)
    
    transaction.total_price = total_price
    transaction.save()

    shipping_info = request.session.get('shipping_info', {})
    payment_method = shipping_info.get("payment_method", "").lower()
    if payment_method == 'paypal':
        request.session['transaction_id'] = transaction.id
        return redirect('process_payment')
    elif payment_method == 'stripe':
        pass
    elif payment_method == 'credit cart':
        pass
    else:
        pass #error

    item_detail = '\n'.join(item_list)
    mail_subject = "New Order Just Arrived"
    message = (
        f"New order has been placed by {request.user.username}.\n"
        f"Transaction ID: {transaction.id}\n"
        f"Total Price: ${transaction.total_price}\n\n"
        f"Items ordered:\n{item_detail}"
    )

    email = EmailMessage(mail_subject, message, to=['dadica.petkovic@gmail.com', request.user.email])
    email.send()

    items_in_cart.delete()
    request.session.pop('shipping_info', None)

    return redirect('payment_done')

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

    shipping_info = request.session.get('shipping_info', {})    
    return render(request, "supplement_store/summary.html", {
        "email": shipping_info.get("email", ""),
        "name": shipping_info.get("first_name", ""),
        "surname": shipping_info.get("last_name", ""),
        "address": shipping_info.get("address", ""),
        "city": shipping_info.get("city", ""),
        "state": shipping_info.get("state", ""),
        "country": shipping_info.get("country", ""),
        "zipcode": shipping_info.get("zipcode", ""),
        "phone": shipping_info.get("phone", ""),
        "payment_method": shipping_info.get("payment_method", ""),
        "items": items,
    })
    # treba da se upali paypal api, stripe api ili api banke u zavisnosti sta sam uzeo kada se klikne buy dugme i to je to ovo je samo provera 

@login_required
def delivery_and_payment(request):
    items = Cart.objects.filter(user=request.user, in_cart=True)
    if not items:
        return redirect('shopping_cart')
    shipping_info = request.session.get('shipping_info', {})
    form = ShippingInformationForm(initial=shipping_info)

    return render(request, "supplement_store/delivery_payment.html", {"form": form})

@login_required
def shopping_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get("id")
        item = Item.objects.get(id=item_id)
        quantity = int(request.POST.get("quantity"))
        if not item.is_available:
            return redirect(request.META.get('HTTP_REFERER', 'index'))
        if quantity is not None and quantity > item.quantity:
            return redirect('shop_by_itemname', fullname=item.fullname)
        Cart.objects.create(user=request.user, item=item, quantity=quantity, in_cart=True)
    cart_items = (
        Cart.objects.filter(in_cart=True, user=request.user)
        .values('item__id', 'item__name', 'item__weight', 'item__price', 'item__sale_price', 'item__main_image', 'item__fullname', 'item__quantity')
        .annotate(total_quantity=Sum('quantity'),total_price=Sum(
            Case(
                When(item__sale_price__isnull=False, then=F('item__sale_price')),
                default=F('item__price'),
                output_field=DecimalField(),
                ) * F('quantity')
            )
        )
    )
    return render(request, "supplement_store/cart.html", {
        "items": cart_items,
    })
    
@login_required    
def remove_cart(request):
    if request.method == 'POST':  
        item = Item.objects.get(id=request.POST["item_id"]) 
        Cart.objects.filter(item=item, user=request.user, in_cart=True).delete()
    return redirect(request.META.get('HTTP_REFERER', 'index'))    

@login_required
def remove_cart_all(request):
    if request.method == 'POST': 
        Cart.objects.filter(user=request.user, in_cart=True).delete()
    return redirect(request.META.get('HTTP_REFERER', 'index'))       

@login_required
def decrease_quantity(request, id):
    cart_item = Cart.objects.filter(item__id=id, user=request.user).first()
    if cart_item and cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def increase_quantity(request, id):
    cart_item = Cart.objects.filter(item__id=id, user=request.user).first()
    if cart_item and cart_item.quantity < cart_item.item.quantity:
        cart_item.quantity += 1
        cart_item.save()
    return redirect(request.META.get('HTTP_REFERER', 'index'))    

def newsletter(request):
    return redirect(request.META.get('HTTP_REFERER', 'index'))

def about(request):
    return render(request, "supplement_store/about.html")

def brands(request):
    return render(request, "supplement_store/brands.html")

def contact(request):
    return render(request, "supplement_store/contact.html")

@login_required
def add_sale_to_item(request):
    if request.user.is_staff or request.user.is_support:
        if request.method == 'POST':
            ids = request.POST.getlist('id')
            sale_prices = request.POST.getlist('sale-price')
            start_dates = request.POST.getlist('sale-date-start')
            end_dates = request.POST.getlist('sale-date-end')
            sale_data = list(zip(ids, sale_prices, start_dates, end_dates))
            for id, price, start, end in sale_data:
                if price:
                    item = Item.objects.get(id=id)
                    item.sale_price = price
                    item.sale_start_date = start
                    item.sale_end_date = end
                    item.save()
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
        context = {
            'categories': Item.CATEGORIES,
            'brands': Item.BRANDS,
        }
        return render(request, "supplement_store/add_item_to_shop.html", context)
    return redirect('index')

def attach_image(field, image_filename):
    if pd.notnull(image_filename):
        source_dir = os.path.join(settings.BASE_DIR, 'supplement_store', 'static', 'supplement_store', 'images', 'product_images')
        full_image_path = os.path.join(source_dir, image_filename)
        if os.path.exists(full_image_path):
            with open(full_image_path, 'rb') as f:
                field.save(os.path.basename(full_image_path), File(f), save=False)
        else:
            print(f"Image not found: {full_image_path}")

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

                attach_image(item.main_image, row['Main Image'])
                attach_image(item.image1, row['Image1'])
                attach_image(item.image2, row['Image2'])
                attach_image(item.image3, row['Image3'])

                item.save()
    return render(request, "supplement_store/add_item_to_shop.html")

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