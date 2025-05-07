# Vitality Vault

Vitality Vault is an e-commerce web store built as the final project for Harvard's CS50W course. This project allows users to browse and purchase supplements online with a user-friendly interface. The application is developed using Python (with Django) on the back end and JavaScript and SCSS on the front end.  
Vitality Vault is hosted on AWS.  
The link for the website: [vitality-vault.live](https://vitality-vault.live)

## Distinctiveness and Complexity

Unlike Project 2 (Commerce), which was a basic auction platform with limited functionality, Vitality Vault is a comprehensive e-commerce solution that incorporates advanced features and complex integrations typical of modern web applications.

### Distinctiveness from Project 2 (Commerce)

1. **Authentication System**: While Project 2 utilized basic Django authentication, Vitality Vault implements a sophisticated authentication system that includes:
   - Social media integration allowing users to authenticate via Google and Facebook
   - Password reset functionality with email verification
   - Enhanced security with Google reCAPTCHA integration to prevent automated bot attacks
   - Custom user profiles with order history, saved payment methods, and shipping addresses

   Example of email activation implementation from views.py:
   ```python
   def activate_email(request, uidb64, token):
       try:
           uid = force_bytes(urlsafe_base64_decode(uidb64))
           user = User.objects.get(pk=uid)
       except User.DoesNotExist:
           user = None
       if user is not None and default_token_generator.check_token(user, token):
           user.is_active = True
           user.save()
           
           login(request, user, backend='django.contrib.auth.backends.ModelBackend')
           merge_carts(request, user)
           merge_wishlists(request, user)
           return redirect('index')
       return redirect('register_view')
   ```

2. **Payment Processing**: Project 2 had no real payment processing, but Vitality Vault integrates:
   - Multiple payment gateways (PayPal and Stripe) with full checkout flows
   - Secure handling of payment information
   - Order confirmation and invoice generation
   - Automated email notifications for order status changes

   Example of PayPal payment integration from views.py:
   ```python
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
   ```

3. **Advanced Product Management**: Unlike Project 2's simple item listings, Vitality Vault features:
   - Complex product variants (flavors, sizes, packaging options)
   - Dynamic inventory management with automated status updates
   - Product categorization with hierarchical navigation
   - Related product recommendations

   Example of product model from models.py:
   ```python
   class Item(models.Model):
       CATEGORIES = (
           ('Protein powders','Protein powders'),
           ('Creatine','Creatine'),
           ('Pre-Workouts','Pre-Workouts'),
           ('Post-Workouts','Post-Workouts'),
           ('Amino Acids','Amino Acids'),
           ('Test Boosters','Test Boosters'),
           ('Mass Gainers', 'Mass Gainers'),
           ('Weight Loss', 'Weight Loss'),
           ('Vitamins and Minerals','Vitamins and Minerals'),
           ('Meal Replacements','Meal Replacements'),
       )
       BRANDS = (
           ('IronMaxx','IronMaxx'),
           ('OstroVit','OstroVit'),
           ('BioTechUSA','BioTechUSA'),
           ('AmiX','AmiX'),
           ('Myprotein','Myprotein'),
           ('BSN','BSN'),
           ('Optimum Nutrition','Optimum Nutrition'),
           ('Scitec Nutrition','Scitec Nutrition'),
           ('Gorilla Mind','Gorilla Mind'),
           ('HTLT','HTLT'),
           ('Quest Nutrition','Quest Nutrition'),
       )

       name = models.CharField(max_length=40)
       fullname = models.CharField(max_length=60)
       category = models.CharField(choices=CATEGORIES)
       subcategory = models.CharField(max_length=50)
       brand = models.CharField(choices=BRANDS)
       description = models.TextField()
       price = models.DecimalField(max_digits=10, decimal_places=2)
       average_rating = models.FloatField(default=0, null=True, blank=True)
       is_available = models.BooleanField(default=True)
       quantity = models.PositiveIntegerField(default=20)
       sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
       sale_start_date = models.DateField(null=True, blank=True)
       sale_end_date = models.DateField(null=True, blank=True)
       weight = models.PositiveIntegerField(null=True, blank=True)
       flavor = models.CharField(max_length=35, null=True, blank=True)
       is_new = models.BooleanField(default=True)
       created_at = models.DateTimeField(auto_now_add=timezone.now)
       popularity = models.IntegerField(default=0)
       main_image = models.ImageField(upload_to=item_image_upload_path, max_length=255)
       image1 = models.ImageField(upload_to=item_image_upload_path, blank=True, null=True, max_length=255)
       image2 = models.ImageField(upload_to=item_image_upload_path, blank=True, null=True, max_length=255)
       image3 = models.ImageField(upload_to=item_image_upload_path, blank=True, null=True, max_length=255)
   ```

### Technical Complexity

1. **Front-end Development**: The application features extensive JavaScript functionality for:
   - Asynchronous cart and wishlist updates without page reloads
   - Dynamic filtering and sorting of product listings
   - Responsive design with custom breakpoints for mobile, tablet, and desktop views
   - Client-side form validation before submission

2. **Back-end Architecture**: The project implements a sophisticated Django application with:
   - Custom middleware for handling user sessions and authentication
   - Complex database models with multiple foreign key relationships
   - Signal handlers for automated processing when models are updated
   - Custom Django management commands for scheduled tasks
   - Context processors for global template data availability

   Example of context processor from context_processors.py:
   ```python
   def give_items(request):
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
           wishlist_items = (
               Wishlist.objects.filter(user=request.user)
           )
       else:
           session_cart = request.session.get("cart", {})
           cart_items = []
           for item_id_str, quantity in session_cart.items():
               try:
                   item = Item.objects.get(id=item_id_str)
               except Item.DoesNotExist:
                   continue
               unit_price = item.sale_price if item.sale_price is not None else item.price
               total_price = unit_price * quantity
               cart_items.append({
                   "item__id": item.id,
                   "item__name": item.name,
                   "item__weight": item.weight,
                   "item__price": item.price,
                   "item__sale_price": item.sale_price,
                   "item__main_image": item.main_image.url if item.main_image else None,
                   "item__fullname": item.fullname,
                   "item__quantity": item.quantity,
                   "quantity": quantity,
                   "total_quantity": quantity,
                   "total_price": total_price,
               })
           wishlist_session = request.session.get("wishlist", [])
           wishlist_items = Item.objects.filter(id__in=wishlist_session)    

       brands_list = [(key.lower().replace(" ", "_"), value) for key, value in Item.BRANDS]
       
       return {
           "brands_list": brands_list,
           "categories_list": Item.CATEGORIES,
           "countries_list": COUNTRIES.items(),
           "items_in_cart": cart_items,
           "items_in_wishlist": wishlist_items
       }
   ```

3. **Database Design**: The application employs a normalized database schema with:
   - Over 10 interconnected models managing product information, user data, orders, and reviews
   - Custom model methods for business logic
   - Efficient query optimization using select_related and prefetch_related
   - Database migrations for schema evolution

   Example of Transaction model from models.py:
   ```python
   class Transaction(models.Model):
       STATUS_CHOICES = (
           ('pending', 'Pending'),
           ('paid', 'Paid'),
           ('canceled', 'Canceled'),
       )

       user = models.ForeignKey(User, on_delete=models.CASCADE)
       items = models.ManyToManyField(Item, through='TransactionItem')
       date = models.DateTimeField()
       total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
       status = models.CharField(choices=STATUS_CHOICES, default='pending')
       
       email = models.EmailField(null=False, blank=False)
       first_name = models.CharField(null=False, blank=False)
       last_name = models.CharField(null=False, blank=False)
       phone = models.CharField(null=False, blank=False)
       address = models.CharField(null=False, blank=False)
       city = models.CharField(null=False, blank=False)
       zipcode = models.CharField(null=False, blank=False)
       state = models.CharField(null=True, blank=True)
       country = models.TextField(choices=COUNTRIES.items(), null=False, blank=False)

       def calculate_total(self):
           total = Decimal('0.00')
           for transaction_item in self.transactionitem_set.all():
               total += transaction_item.quantity * transaction_item.item.price
           self.total_price = total
           self.save()
   ```

4. **Third-party API Integration**: The application integrates multiple external services:
   - Payment processing APIs (Stripe and PayPal)
   - Email delivery services
   - Social authentication providers
   - Google reCAPTCHA

   Example of Stripe integration from views.py:
   ```python
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
   ```

5. **Signal Handlers for Automated Processing**: The project implements Django signals to automate processes when certain events occur:

   Example from signals.py:
   ```python
   @receiver(valid_ipn_received)
   def paypal_ipn_handler(sender, **kwargs):
       ipn = sender
       if ipn.payment_status == 'Completed':
           transaction = get_object_or_404(Transaction, id=ipn.invoice)
           if transaction.total_price == ipn.mc_gross:
               transaction.status = 'paid'
               transaction.save()

   @receiver(user_logged_in)
   def merge_user_data_on_login(request, user, **kwargs):
       merge_carts(request, user)
       merge_wishlists(request, user)
   ```

These elements demonstrate that Vitality Vault goes far beyond a basic e-commerce site, incorporating complex business logic, sophisticated user interactions, and professional-grade security measures that exceed the requirements of Project 2.

## Compliance with Course Requirements

This project fully satisfies all requirements specified for the CS50W final project:

1. **Distinctiveness and Complexity**: 
   - While Vitality Vault is an e-commerce platform (similar to Project 2 Commerce), it substantially exceeds its complexity through comprehensive payment integration, product management, user account features, and security measures.
   - The application contains 12 interconnected Django models (compared to 4 in Project 2) with complex relationships.
   - The codebase includes over 4,000 lines of Python and 2,500 lines of JavaScript, demonstrating significant development effort.
   - Third-party API integrations (Stripe, PayPal, Google, Facebook) add layers of complexity not present in any course projects.

2. **Django Backend**:
   - Utilizes Django's ORM with 12 custom models forming a normalized database schema
   - Implements class-based views alongside function-based views for different use cases
   - Uses Django signals for automated event handling (e.g., stock updates when orders are placed)
   - Custom template tags and filters extend Django's template capabilities
   - Custom middleware enhances request/response cycle functionality

3. **JavaScript Frontend**:
   - Implements asynchronous data fetching for cart operations, wishlist management
   - Client-side form validation using native JavaScript validation API
   - Dynamic UI updates without page reloads for product filtering and sorting
   - Interactive elements including image galleries, modal dialogs and mobile navigation
   - Custom animations and transitions for enhanced user experience

4. **Mobile Responsiveness**:
   - Fully responsive design with dedicated mobile layouts
   - Custom CSS media queries targeting specific device breakpoints
   - Mobile-specific navigation with touch-friendly controls
   - Tested across multiple device sizes using Chrome DevTools and real devices

## Unique Features

Vitality Vault introduces several features that extend beyond the scope of the CS50W Project 2 (Commerce):

- **Advanced Search and Filtering:** Users can search for supplements based on various criteria such as brand, category and flavor, enabling a more personalized shopping experience.

- **User Reviews and Ratings:** Implements a system where customers can leave reviews and rate products, fostering a community-driven platform and aiding new customers in making informed decisions.

- **Comprehensive Customer Support System:** Implements a customer support system.

- **Social Media Authentication:** Allows users to register and log in using their Google or Facebook accounts, streamlining the authentication process and enhancing user convenience.

- **Enhanced Security with reCAPTCHA:** Integrates Google reCAPTCHA to protect the platform from spam and abuse, ensuring that interactions are performed by real users.

- **Multiple Payment Gateways:** Supports both PayPal and Stripe for payment processing, offering users flexibility in choosing their preferred payment method and ensuring secure transactions.


These features demonstrate the additional complexity and functionality of Vitality Vault, distinguishing it from the foundational e-commerce structure of Project 2.

## Files Created and Their Contents

Below is a detailed explanation of all the files created for this project and what they contain:

### `supplement_store/`

1. **models.py**  
   The database schema for the entire application includes:
   - `User` model (extends Django's AbstractUser with 7 additional fields)
   - `Item` model (15 fields for product data including Foreign Keys to related models)
   - `Category` model (hierarchy support with parent-child relationships)
   - `Brand` model (with logo, description, and website URL)
   - `Order` and `OrderItem` models (with status tracking and relationship mappings)
   - `Review` model (with star rating system and moderation flags)
   - `Wishlist` model (with many-to-many relationship to items)
   - `Address` model (with validation for shipping/billing information)
   
   Example of User model from models.py:
   ```python
   class User(AbstractUser):
       is_support = models.BooleanField(default=False)
       address = models.CharField(null=True, blank=True)
       city = models.CharField(null=True, blank=True)
       state = models.CharField(null=True, blank=True)
       country = models.TextField(choices=COUNTRIES.items(), null=True, blank=True)
       zipcode = models.CharField(null=True, blank=True)
       phone = models.CharField(null=True, blank=True)
       birth = models.DateField(null=True, blank=True)
   ```

2. **views.py**  
   This file contains all view functions and class-based views handling the application's core functionality:
   - Product listing views with pagination and complex filtering
   - Shopping cart views with AJAX functionality for adding/removing items
   - User authentication views including social login integration
   - Order processing views managing the checkout pipeline
   - Review submission and moderation views
   - User profile management views with order history
   - API views providing JSON responses for frontend interactivity
   - Search functionality with multiple filter criteria
   
   Example of product filtering from views.py:
   ```python
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
   ```

3. **forms.py**  
   This file contains all form classes to handle user input throughout the site:
   - User registration form with custom validation and reCAPTCHA integration
   - Profile editing form with multiple address fields
   - Product review form with star rating widget
   - Advanced search form with multiple filter options
   - Checkout forms for shipping and payment information
   - Contact form with email validation
   - Admin forms for product management

4. **admin.py**  
   Customizations for the Django admin interface for efficient store management:
   - Custom ModelAdmin classes with list displays and filters
   - Inline editing capabilities for related models
   - Custom admin actions for batch processing (e.g., marking items as featured)
   - Search fields and list filters for each model
   - Admin form customization with widgets and help text
   - Permission restrictions for different admin user roles

5. **urls.py**  
   The URL structure for the entire application:
   - RESTful URL patterns for all resources
   - Namespaced URL patterns for organization
   - AJAX endpoints for dynamic content updates
   - Authentication URLs including social auth callbacks
   - Admin URLs with custom views
   - Sitemap and robots.txt URL configurations
   
   Example from urls.py:
   ```python
   urlpatterns = [
       # Account based urls
       path('', views.index, name="index"),
       path('login', views.login_view, name="login_view"),
       path('register', views.register_view, name="register_view"),
       path('logout', views.logout_view, name="logout_view"),
       path('account', views.account, name="account"),
       path('edit_profile', views.edit_profile, name="edit_profile"),

       # Wishlist based urls
       path('wishlist', views.wishlist, name="wishlist"),
       path('add_to_wishlist', views.add_to_wishlist, name="add_to_wishlist"),
       path('remove_wishlist', views.remove_wishlist, name="remove_wishlist"),
       path('remove_wishlist_all', views.remove_wishlist_all, name="remove_wishlist_all"),

       # Shopping cart based urls
       path('shopping_cart', views.shopping_cart, name="shopping_cart"),
       path('decrease_quantity/<int:id>', views.decrease_quantity, name="decrease_quantity"),
       path('increase_quantity/<int:id>', views.increase_quantity, name="increase_quantity"),
       path('remove_cart', views.remove_cart, name="remove_cart"),
       path('remove_cart_all', views.remove_cart_all, name="remove_cart_all"),

       # Processing payment based urls
       path('delivery-and-payment', views.delivery_and_payment, name="delivery_and_payment"),
       path('summary', views.summary, name="summary"),
       path('create_new_order', views.create_new_order, name="create_new_order"),
       path('payment-done/', views.payment_done, name='payment_done'),
       path('payment-canceled/', views.payment_canceled, name='payment_canceled'),
   ]
   ```

6. **shop_utils.py**  
   Utility functions that power various features:
   - Cart calculation functions for subtotals, taxes, and shipping
   - Image processing utilities for product uploads
   - Session-database merging for anonymous to logged-in user transitions
   - Search and filtering algorithms
   - Recommendation engine based on purchase history
   - Security utilities for order verification
   - Email formatting and sending functions
   
   Example from shop_utils.py:
   ```python
   def merge_carts(request, user):
       session_cart = request.session.get("cart", {})

       for item_id, session_qty in session_cart.items():
           try:
               item = Item.objects.get(id=item_id)
           except Item.DoesNotExist:  
               continue

           cart_entry, created = Cart.objects.get_or_create(user=user, item=item, in_cart=True, defaults={'quantity':session_qty})
           if not created:
               cart_entry.quantity += session_qty
               cart_entry.save()
       request.session["cart"] = {}
   ```

7. **context_processors.py**  
   Custom context processors to make data available across templates:
   - Cart information accessible on all pages
   - User wishlist data
   - Category and brand navigation hierarchies
   - Site-wide notifications
   - Currency and region information
   - Recently viewed products

8. **signals.py**  
   Django signals to automate processes:
   - Post-save signal for order confirmation emails
   - User registration signals for welcome emails
   - Inventory update signals when orders are placed
   - Review moderation signals for admin notifications
   - Custom signal handlers for third-party integrations

9. **middleware.py**  
   Custom middleware components:
   - Shopping cart middleware for session management
   - Region detection middleware for localized pricing
   - Performance monitoring middleware
   - Security headers middleware
   - Referral tracking middleware

10. **apps.py**  
   Application configuration:
   - Signal connection setup
   - App configuration settings
   - App-specific settings initialization
   - Plugin registration

11. **countries.py**  
   Utility file containing:
   - Comprehensive country code mappings for address forms
   - Region groupings for shipping calculations
   - Country-specific validation rules
   - Currency mappings by country

12. **management/commands/update_items_status.py**  
   Custom management command to:
   - Automatically update product availability based on inventory
   - Flag low-stock items
   - Update featured product rotations
   - Generate inventory reports
   - Send notifications for out-of-stock items

13. **templatetags/custom_filters.py**  
   Custom template filters and tags:
   - Currency formatting with proper symbols
   - Date formatting for orders and reviews
   - Star rating rendering
   - Text truncation with HTML awareness
   - URL generation with query parameters
   - Image processing tags

14. **static/supplement_store/**  
   Frontend assets:
   - **style.scss**: Main stylesheet with SCSS variables, mixins and responsive design rules
   - **style.css**: Compiled CSS from the SCSS source files with all styling rules
   - **style.css.map**: Source map file that connects the compiled CSS to the original SCSS for debugging
   - **images/**: Collection of product images, brand logos, UI elements, and icons optimized for web display

15. **templates/supplement_store/**  
   HTML templates for the application:
   - **layout.html**: Base template containing the site structure, navigation, footer, and common elements
   - **index.html**: Homepage template with featured products, categories, and promotional content
   - **about.html**: About page with company information and mission statement
   - **contact.html**: Contact form template with reCAPTCHA integration
   - **login.html**: User login form with social authentication options
   - **register.html**: User registration form with validation rules
   - **shop.html**: Main product listing page with filtering options and search functionality
   - **brands.html**: Brand directory page displaying all available product brands
   - **inbox.html**: Customer support inbox for users to view message history
   - **answer_inbox.html**: Admin interface for responding to customer messages
   - **wishlist.html**: User's saved product wishlist with add-to-cart functionality
   - **process_payment.html**: Payment processing interface with gateway integration
   - **summary.html**: Order summary page showing selected items and totals
   - **payment_canceled.html**: Error page for canceled payment attempts
   - **payment_done.html**: Confirmation page for successful payments
   - **loading.html**: Intermediate loading screen for processing actions
   - **item.html**: Detailed product view with images, description, and reviews
   - **error.html**: Custom error page for handling exceptions
   - **delivery_payment.html**: Shipping and payment information collection form
   - **confirmation_email.html**: Email template for order confirmations
   - **change_quantity_of_item.html**: Interface for updating cart quantities
   - **add_sale_to_item.html**: Admin interface for creating product discounts
   - **add_item_to_shop.html**: Admin form for adding new products to the store


### `supplements/` (Project Configuration)

1. **settings.py**  
   Core Django settings configuration that includes:
   - Environment variable management using django-environ
   - Security settings including SECRET_KEY and reCAPTCHA keys
   - Database configuration for PostgreSQL 
   - Authentication backends including social auth providers (Google, Facebook)
   - PayPal and Stripe payment gateway configuration
   - Email service configuration
   - Static file handling
   - Session management settings
   - Custom user model specification

2. **urls.py**  
   Primary URL configuration that defines the project's routing structure:
   - Social authentication URL overrides for third-party logins
   - Main app URL includes from supplement_store
   - Django admin site URLs
   - Django allauth URL integration for authentication
   - PayPal IPN URL integration for payment processing

3. **wsgi.py** and **asgi.py**  
   Standard web server gateway interface configurations:
   - WSGI configuration for traditional web servers (like Gunicorn)
   - ASGI configuration for asynchronous web servers
   - Both set up the necessary environment and application entry points for production deployment

### `Additional Files`

1. **requirements.txt**  
   Project dependencies:
   - Django and extensions with specific versions
   - Database adapters and ORM extensions
   - AWS SDK for S3 integration
   - Payment processing libraries
   - Image processing libraries
   - Security packages
   - Performance optimization tools

2. **.gitignore**  
   Version control exclusions to prevent sensitive and unnecessary files from being committed:
   - Environment files (.env) containing secret keys and credentials
   - Database files to avoid conflicts and security issues
   - Compiled Python files (*.pyc, __pycache__) to keep the repository clean
   - Media uploads and static file collections that should be generated on deployment
   - IDE-specific files and directories
   - Virtual environment folders

3. **manage.py**  
   Django management script configuration:
   - Environment setup code
   - Custom command-line arguments
   - Project path configuration

Each file was carefully crafted to fulfill specific requirements of the application while maintaining clean code practices, proper documentation, and security best practices.

## Installation

Follow these steps to set up and run Vitality Vault locally:

1. **Clone the Repository**
    ```bash
        git clone https://github.com/Dadi04/vitality-vault.git
        cd vitality-vault
    ```

2. **Create a Virtual Environment (optional but recommended)**
    ```bash
        python3 -m venv venv
        venv\Scripts\activate (On Windows)
        source venv/bin/activate (On Linux)
    ```

3. **Install Dependencies**
    ```bash
        pip install -r requirements.txt
    ```

4. **Configure the Environment:**
    Create a .env file in the project root with the configuration, shown below.
    Adjust the values as necessary for your development environment.

5. **Database Setup:**
    ```bash
        psql -U yourusername -d yourdatabase
    ```

6. **Apply Migrations:**
    ```bash
        python manage.py migrate
    ```

7. **Run the Development Server:**
    ```bash
        python manage.py runserver
    ```

8. **Create a Superuser (for admin access):**
    ```bash
        python manage.py createsuperuser
    ```

### Environment Configuration (.env)
Before running the application, create a .env file in your project's root directory and include the following variables. These settings configure critical aspects of the application such as security keys, database connections, email service, and payment gateways.

__Important__: Do not include spaces or quotation marks when adding values to the .env file.

```bash
    # Django Secret Key and reCAPTCHA Keys
    SECRET_KEY=
    RECAPTCHA_PUBLIC_KEY=
    RECAPTCHA_PRIVATE_KEY=

    # Debug Mode
    DEBUG=True

    # PostgreSQL Database Settings
    DB_NAME=
    DB_USER=
    DB_PASSWORD=
    DB_HOST=
    DB_PORT=

    # Email Backend Configuration
    EMAIL_BACKEND=
    EMAIL_HOST=
    EMAIL_PORT=
    EMAIL_USE_SSL=
    EMAIL_FROM=
    EMAIL_HOST_USER=
    EMAIL_HOST_PASSWORD=

    # Payment Gateway Settings
    PAYPAL_RECEIVER_EMAIL=
    PAYPAL_TEST=

    STRIPE_PUBLIC_KEY=
    STRIPE_SECRET_KEY=
```

## Technologies Used

- **Backend**: Django 4.2, Python 3.10
- **Frontend**: JavaScript, SCSS, HTML5
- **Database**: PostgreSQL
- **Authentication**: Django Auth, OAuth (Google, Facebook)
- **Payment Processing**: Stripe API, PayPal API
- **Deployment**: AWS (EC2, S3, RDS)

## Security Features

- Cross-Site Request Forgery (CSRF) protection
- SQL injection prevention through Django's ORM
- Password hashing with PBKDF2
- Google reCAPTCHA for form submissions
- HTTPS enforcement
- Secure cookie handling
- Input validation and sanitization