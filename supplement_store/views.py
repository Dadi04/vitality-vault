import json
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.forms import SetPasswordForm
from django.http import JsonResponse
from django.db.models import Subquery, OuterRef, F, Avg, Sum

from datetime import datetime

from .forms import RegistrationForm
from .countries import COUNTRIES
from .models import User, SlideShowImage, Support, SupportAnswer, Item, Review, Cart

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
        # get the info from the user
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

            # create the user
            user = User.objects.create_user(username=username, email=email, password=password, first_name=first, last_name=last, phone=phone, birth=birthday, address=address, city=city, state=state, country=country, zipcode=zipcode)
            user.is_active = False
            user.save()

            # popraviti ovo tako da ne saveuje odmah user u databazu nego tek kad on klikne na mail
            # napraviti neki password security da ne moze bas tipa 1234

            # emailing logic
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
    items = Item.objects.filter(weight__isnull=False).order_by('name', '-is_available')
    
    categories = []
    subcategories = []
    flavors = []
    brands = []
    unique_items = {}
    final_items = []

    for item in items:
        if item.fullname not in unique_items:
            unique_items[item.fullname] = item
            final_items.append(item) 
        elif item.is_available:
            unique_items[item.name] = item

        if item.category not in categories:
            categories.append(item.category)
        if item.flavor not in flavors:
            flavors.append(item.flavor)
        if item.brand not in brands:
            brands.append(item.brand)
        if item.subcategory not in subcategories:
            subcategories.append(item.subcategory)

    context_json = json.dumps(items, default=str)

    return render(request, "supplement_store/shop.html", {
        "items": final_items,
        "categories": categories,
        "subcategories": subcategories,
        "flavors": flavors,
        "brands": brands,
        "context_json": context_json,
    })

def shop_by_category(request, category):
    items_by_category = Item.objects.filter(category=category).order_by('name', '-is_available')

    categories = []
    subcategories = []
    flavors = []
    brands = []
    unique_items = {}
    final_items = []

    for item in items_by_category:
        average_review = Review.objects.filter(item=Item.objects.filter(fullname=item.fullname).first()).aggregate(Avg('rating'))['rating__avg']
        if item.fullname not in unique_items:
            unique_items[item.fullname] = item
            item.average_rating = average_review
            item.save()
            final_items.append(item) 
        elif item.is_available:
            unique_items[item.name] = item

        if item.category not in categories:
            categories.append(item.category)
        if item.flavor not in flavors:
            flavors.append(item.flavor)
        if item.brand not in brands:
            brands.append(item.brand)
        if item.subcategory not in subcategories:
            subcategories.append(item.subcategory)    

    return render(request, "supplement_store/shop.html", {
        "items": final_items,
        "categories": categories,
        "subcategories": subcategories,
        "flavors": flavors,
        "brands": brands,
    })

def shop_by_brand(request, brand):
    items_by_brand = Item.objects.filter(brand=brand).order_by('name', '-is_available')

    unique_items = {}
    final_items = []

    for item in items_by_brand:
        average_review = Review.objects.filter(item=Item.objects.filter(fullname=item.fullname).first()).aggregate(Avg('rating'))['rating__avg']
        if item.fullname not in unique_items:
            unique_items[item.fullname] = item
            item.average_rating = average_review
            item.save()
            final_items.append(item) 
        elif item.is_available:
            unique_items[item.name] = item

    categories = Item.objects.filter(brand=brand).values_list('category', flat=True).distinct()
    subcategories = Item.objects.filter(brand=brand).values_list('subcategory', flat=True).distinct()
    flavors = Item.objects.filter(brand=brand).values_list('flavor', flat=True).distinct()
    brands = Item.objects.filter(brand=brand).values_list('brand', flat=True).distinct()

    return render(request, "supplement_store/shop.html", {
        "items": final_items,
        "categories": categories,
        "subcategories": subcategories,
        "flavors": flavors,
        "brands": brands,
    })

def shop_by_itemname(request, itemname):
    items = Item.objects.filter(fullname=itemname).distinct('flavor')
    items_json = json.dumps([item.serialize() for item in items], default=str)
    reviews = Review.objects.filter(item=Item.objects.filter(fullname=itemname).first()).order_by('-timestamp')
    average_review = reviews.aggregate(Avg('rating'))['rating__avg']

    return render(request, "supplement_store/item.html", {
        "items": items,
        "items_json": items_json,
        "reviews": reviews,
        "average_review": average_review
    })

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
    return render(request, "supplement_store/wishlist.html")

@login_required
def shopping_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get("id")
        item = Item.objects.get(id=item_id)
        quantity = int(request.POST.get("quantity", 1))
        if quantity is not None and quantity > item.quantity:
            return redirect('shop_by_itemname', fullname=item.fullname)
        if not item.is_available:
            return redirect(request.META.get('HTTP_REFERER', 'index'))
        
        Cart.objects.create(user=request.user, item=item, quantity=quantity, in_cart=True)
    cart_items = (
        Cart.objects.filter(in_cart=True, user=request.user).values('item__id', 'item__name', 'item__weight', 'item__price', 'item__main_image', 'item__fullname', 'item__quantity')
        .annotate(total_quantity=Sum('quantity'),total_price=Sum(F('item__price') * F('quantity')))
    )
    return render(request, "supplement_store/cart.html", {
        "items": cart_items,
    })
    
def remove_cart(request):
    if request.method == 'POST':  
        item = Item.objects.get(id=request.POST["item_id"]) 
        Cart.objects.filter(item=item, user=request.user, in_cart=True).delete()
    return redirect(request.META.get('HTTP_REFERER', 'index'))    

def decrease_quantity(request, id):
    cart_item = Cart.objects.filter(item__id=id, user=request.user).first()
    if cart_item and cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    return redirect(request.META.get('HTTP_REFERER', 'index'))
        
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
    if request.user.is_staff == True or request.user.is_support == True:
        latest_message_subquery = Support.objects.filter(user=OuterRef('user')).order_by('-date').values('message')[:1]
        one_message_per_user = Support.objects.annotate(latest_message=Subquery(latest_message_subquery)).filter(message=F('latest_message'), is_closed=False)
        messages = one_message_per_user.all()
        return render(request, "supplement_store/inbox.html", {
            "messages": messages
        })
    else: 
        return redirect('index')

@login_required
def answer_inbox(request, username):
    if request.user.is_staff == True or request.user.is_support == True:
        user = User.objects.get(username=username)
        support_messages = Support.objects.filter(user=user, is_closed=False)
        answer_messages = SupportAnswer.objects.filter(latest_message__in=support_messages, latest_message__is_closed=False)

        combined_messages = list(support_messages) + list(answer_messages)
        sorted_messages = sorted(combined_messages, key=lambda x: x.date, reverse=True)

        return render(request, "supplement_store/answer_inbox.html", {
            "messages": sorted_messages,
            "username": username
        })
    else: 
        return redirect('index')

@login_required
def close(request, username):
    if request.user.is_staff == True or request.user.is_support == True:
        user = User.objects.get(username=username)
        all_support_messages = Support.objects.filter(user=user)
        for support in all_support_messages:
            support.is_closed = True
            support.save()
        all_answer_messages = SupportAnswer.objects.filter(latest_message__in=all_support_messages)
        for answer in all_answer_messages:
            answer.latest_message.is_closed = True
            answer.save()

        return redirect('inbox')
    else:
        return redirect('index')

@login_required
def answering(request, username):
    if request.user.is_staff == True or request.user.is_support == True:
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
    else: 
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
    




    
# upitno, morace js, yt ili chatgpt
#def filter_products(request):
#    selected_categories = request.GET.getlist('category')
#    selected_subcategories = request.GET.getlist('subcategory')
#    selected_flavors = request.GET.getlist('flavor')
#    selected_brands = request.GET.getlist('brand')
#    filtered_products = None
#
#    if selected_categories:
#        filtered_products = Item.objects.filter(category__in=selected_categories).order_by('fullname', '-is_available')
#    if selected_subcategories:
#        filtered_products = Item.objects.filter(subcategory__in=selected_subcategories).order_by('fullname', '-is_available')    
#    if selected_flavors:
#        filtered_products = Item.objects.filter(flavor__in=selected_flavors).order_by('fullname', '-is_available')
#    if selected_brands:
#        filtered_products = Item.objects.filter(brand__in=selected_brands).order_by('fullname', '-is_available')    
#
#    if filtered_products:
#        unique_items = {}
#        final_items = []
#        categories = []
#        subcategories = []
#        flavors = []
#        brands = []
#
#        for item in filtered_products:
#            if item.fullname not in unique_items:
#                unique_items[item.fullname] = item
#                final_items.append(item) 
#            elif item.is_available:
#                unique_items[item.name] = item
#            if item.category not in categories:
#                categories.append(item.category)
#            if item.flavor not in flavors:
#                flavors.append(item.flavor)
#            if item.brand not in brands:
#                brands.append(item.brand)    
#            if item.subcategory not in subcategories:
#                subcategories.append(item.subcategory)       
#        print(final_items)
#        return render(request, "supplement_store/shop.html", {
#            "items": final_items,
#            "categories": categories,
#            "subcategories": subcategories,
#            "flavors": flavors,
#            "brands": brands,
#        })
#    else:
#        messages.error(request, "Please select a filter")
#        return redirect(request.META.get('HTTP_REFERER', 'index'))
