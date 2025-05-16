# Vitality Vault

Vitality Vault is an e-commerce web store built as the final project for Harvard's CS50W course. This project allows users to browse and purchase supplements online with a user-friendly interface. The application is developed using Python (with Django) on the back end and JavaScript and SCSS on the front end.  
Vitality Vault is hosted on AWS.  
The link for the website: [vitality-vault.live](https://vitality-vault.live)

## Distinctiveness and Complexity

Vitality Vault goes well beyond the baseline requirements of CS50W’s Project 2 by integrating numerous advanced features, architectural patterns and third-party services that demonstrate both distinctiveness and depth of implementation. At its core, the application is not simply a CRUD store, but a fully featured e-commerce platform with complex workflows for search, filtering, authentication, transaction management, customer support and automated maintenance. The combination of these modules—and the nontrivial interactions between them—epitomizes the level of complexity and originality expected for a final project.

Vitality Vault introduces several features that extend beyond the scope of the CS50W Project 2 (Commerce):

- **Advanced Search and Filtering:** 
Users can search for supplements based on various criteria such as brand, category, subcategory and flavor, enabling a more personalized shopping experience.

- **Real Customer Reviews and Ratings:** 
Shoppers can leave written reviews and star ratings and our system automatically calculates average scores.

- **Comprehensive Customer Support System:** 
Instead of emailing the store owner directly, customers submit support tickets right on the site.
Staff members have a threaded inbox view—no third-party helpdesk needed—complete with status flags, timestamps and email notifications.
The reason I built this in-app ticketing workflow because I wanted users to reach our support team with a single click—no opening external email clients required.

- **Smooth Social Logins:** 
New users can sign up or log in using Google or Facebook in just a couple of clicks—no extra passwords to remember. Behind the scenes, Django Allauth and secure OAuth flows keep everything safe and seamless.
Spam and bots are kept at bay with Google reCAPTCHA, so the accounts are all real people.
If they dont want to use neither Google or Facebook, they can opt for a custom authentication solution.

- **Multiple Payment Gateways:** 
Customers choose between PayPal or Stripe at checkout, combining the convenience and wide credit-card support of both PayPal and Stripe.
Project handles sensitive keys and webhooks securely, so payment updates arrive in real time and order statuses always stay accurate.

- **Automation and Maintenance** 
A custom management command automatically retires “New” badges after 30 days and cleans up expired sales, keeping the catalog fresh without any manual effort.
Cron‐driven tasks and Django signals work behind the scenes, so inventory levels, sale prices and product flags are always up to date.
One of the reasons I implemented these background tasks is to fully automate badge removal and sale expiration, so I never have to perform those tedious updates by hand.

- **Robust Admin & Support Tools**
The site includes a full suite of staff and support interfaces to manage products, promotions, sales and customer communications without touching the database directly, more of this later in [views.py](#staff--support-tooling-based-views) file.
I created this custom UI because I didn’t want to expose sensitive customer data (like addresses and phone numbers) in the default Django admin—or risk anyone poking directly at the database.

These features demonstrate the additional complexity and functionality of Vitality Vault, distinguishing it from other projects from the course.

## Files Created and Their Contents

Below is a detailed explanation of all the files created for this project and what they contain:

### `supplement_store/`

1. **models.py**
   This file contains database schema for the entire application includes:
   - `User` - extends Django's AbstractUser to add is_support flag and profile details
   - `Item` - represents a product with categorization, pricing, inventory, metadata (used for filtering) and up to four images
   - `Suport` - tracks customer support requests with a link to the submitting user (ForeignKey to User model), timestamp, message content and status flags (answered, closed)
   - `SupportAnswer` - records responses to support requests, linking back to the original Support entry (ForeignKey to User model), the staff user who answered, the response text and the response timestamp
   - `SlideShowImage` - stores images for a homepage slideshow
   - `Review` - captures a user's (ForeignKey to User model) text review and numeric rating for a product (ForeignKey to Item model), with a timestamp of when it was submitted
   - `Cart` - represents a user's cart entry, linking a user (ForeignKey to User model) to a product (ForeignKey to Item model) with a specified quantity
   - `Wishlist` - records items that a user has wish‐listed, linking each user (ForeignKey to User model) to a specific product (ForeignKey to Item model)
   - `Transaction` - logs an order placed by a user, with many-to-many products through TransactionItem model, along with billing/shipping info, total price, status (pending/paid/canceled) and timestamp
   - `TransactionItem` - the through‐model linking a Transaction model to each product purchased, recording the quantity of that item for the transaction
   - `Newsletter` - holds email addresses of users who have subscribed to the site's newsletter

2. **views.py**  
   This file contains all view functions and class-based views handling the application's core functionality:
   - `index` - renders the homepage with slideshow images ordered by their display priority, current sale items, new arrivals and top 10 popular items
   - `about` - renders the static about.html page template
   - `brands` - renders the static brands.html page template
   - `contact` - on POST reqest sends an email to the store owner using submitted title, body and sender address, then renders the contact page
    
       ###### Account-based views
   - `login_view` - authenticates a user by username or email, manages “remember me” session expiry, merges any guest cart and wishlist into the user's account and redirects on success or failure
   - `register_view` - processes new user registration via a RegistrationForm, creates an inactive user, sends an email activation link and displays a loading page
   - `activate_email` - validates the email activation token, activates and logs in the corresponding user, merges carts and wishlists and redirects to the homepage
   - `logout_view` - logs out the current user and redirects to the homepage
   - `comment` - lets a logged-in user submit a text review and rating for an item, saving it as a review and returning to the referring page if both fields are provided, used in item.html template
   - `account` -  retrieves the current user's past transactions and their associated items and renders the account page
   - `edit_profile` - updates the logged-in user's profile fields (email, address, phone, birth date, etc.) and redirects back to the account page, used in account.html
   
       ###### Filtering views
   - `supplements` - filters, sorts, annotates with wishlisted status, paginates and renders all items based on query parameters for shop browsing
   - `shop_by_category` - filters items by a given category, then applies the same filtering, sorting, wishlisted annotation and pagination as in supplements
   - `shop_by_brand` - filters items by a given brand, then applies the same filtering, sorting, wishlisted annotation and pagination as in supplements
   - `shop_by_itemname` - retrieves the first available flavor per item fullname, annotates wishlisted state, selects a variant, finds similar items (based on subcategory), loads reviews and averages and renders the selected item page
   - `search_items` - returns up to five popular items matching a free-text query by name, brand or category as JSON

        ###### Wishlist views
   - `wishlist` - displays the logged-in user's saved wishlist entries or reconstructs them from session data for anonymous visitors
   - `add_to_wishlist` - adds an item to the user's wishlist in the database or session (if user is not logged in) on POST request and redirects back to the same page
   - `remove_wishlist` - removes a specific item from the user's wishlist in the database or session (if user is not logged in) on POST request and redirects back to the same page
   - `remove_wishlist_all` - clears all wishlist entries for the current user or session (if user is not logged in) on POST request and redirects back to the same page, used in wishlist.html

        ###### Shopping cart views
   - `shopping_cart` - on POST request, adds a specified quantity of an item to the cart in the database or session (if user is not logged in); on GET request, compiles and annotates cart items with totals and renders the cart page
   - `remove_cart` - deletes a single cart entry in the database or session (if user is not logged in) on POST request and redirects back to the same page
   - `remove_cart_all` - empties the entire cart in the database or session (if user is not logged in) on POST request and redirects back to the same page, used in cart.html
   - `decrease_quantity` - decrements the quantity of a cart item in the database or session (if user is not logged in), removing it entirely if it hits zero and redirects back to the same page
   - `increase_quantity` - increments the quantity of a cart item in the database or session (if user is not logged in), respecting available stock and redirects back to the same page

        ###### Purchase & transaction views
   - `delivery_and_payment` - ensures the user has items in the cart, retrieves any saved shipping info and renders the delivery and payment form
   - `summary` - shows a summary of shipping details and cart items, saving shipping info into the session if provided
   - `create_new_order` - converts the current cart into a transaction with transaction items, saves billing and shipping info and initiates either PayPal or Stripe checkout
   - `payment_done` - marks the transaction as paid, updates item stock and popularity, sends email confirmation, clears the cart and session and shows a success page
   - `payment_canceled` - marks a pending transaction as canceled if it exists, clears session data and displays a cancellation page

        ###### Staff & support tooling-based views
   - `newsletter` - adds an email to the newsletter list if not already present, otherwise shows an error, then redirects back to the same page
   - `send_email_to_newsletter` - for staff or support users, sends a bulk email with a provided title and body to all subscribed newsletter addresses
   - `add_sale_to_item` - for staff or support users, updates stock quantities for selected items and re-renders the quantity management page
   - `change_quantity_of_item` - renders the item-creation form for staff or support users, redirecting non-staff to home page
   - `add_item_to_shop` - renders the item-creation form for staff or support users, redirecting non-staff to home page
   - `add_item` - for staff or support users, processes an ItemForm submission with images to create a new store item and redirects back to the add-item page
   - `bulk_add_items` - for staff or support users, ingests an uploaded Excel file of item data, updates existing items or creates new ones (including images) and re-renders the add-item page

        ###### Messaging-based views
   - `chatting` - saves a new support message from the logged-in user via POST request and returns JSON success or error
   - `inbox` - for staff or support users, lists each user’s most recent open support request for a compact inbox view
   - `answer_inbox` - for staff or support users, fetches and interleaves a user’s open support and support answer messages in date order for a threaded reply interface
   - `close` - marks all of a given user’s support requests and answers as closed for staff or support users and redirects home
   - `answering` - lets staff or support users post an answer to a user’s latest open support message, marking it answered and returning to the threaded view
   - `load_messages` - via GET request, returns the logged-in user’s open support requests and answers in chronological order as JSON

   - `CustomPasswordResetView` - validates that the submitted email belongs to an existing user before sending reset instructions and redirects to the "password reset done" page on success
   - `CustomPasswordResetConfirmView` - ensures the two new-password fields match before setting the user’s password, updates the session auth hash to keep them logged in and then proceeds with the standard confirmation flow

3. **forms.py**  
   This file contains all form classes to handle user input throughout the site:
    - `RegistrationForm` – defines fields and validation for new user signup, including email, username, profile details, password confirmation and reCAPTCHA verification
    - `ItemForm` – a ModelForm for creating or editing Item instances with all relevant product fields (name, category, pricing, inventory, images, etc.)
    - `ShippingInformationForm` – collects and validates shipping and payment details (contact info, address, country and chosen payment method) during checkout

4. **admin.py**  
    This file registers all of models with Django's admin interface for site administration

5. **urls.py**
    Declares all store-related routes (products, cart actions, auth, messaging, etc.) using path().

6. **shop_utils.py**  
   Collection of helpers for query-building, sorting, review-data attachment, image assignment and merging session data into persistent Cart/Wishlist models.

7. **context_processors.py**  
   Supplies templates with cart and wishlist items (from the DB or session), plus brand, category and country lists.

8. **signals.py**  
   Hooks into PayPal IPN and Allauth login events to mark transactions as paid and merge session carts/wishlists into the user’s account.

9. **apps.py**  
   Registers the supplement_store app and imports its signal handlers on startup via ready().

10. **countries.py**  
   Complete dictionary of country codes and names with all countries. Used throughout the application (in views.py, models.py, forms.py and context_processors.py) for address forms and shipping options

11. **management/commands/update_items_status.py**  
   Custom Django management command for product lifecycle automation:
   - Automatically removes "is_new" flag from products after 30 days
   - Handles product sale periods by managing start and end dates
   - Cleans up expired sales by removing sale prices when sales end
   - Scheduled via cron jobs for regular maintenance
   - Provides informative console output for tracking changes

12. **templatetags/custom_filters.py**  
   Collection of specialized template filters that extend Django's template language:
   - `filename`: Extracts filenames from file paths
   - `change`: Replaces '%' characters with '_' for URL safety
   - `star_range`: Generates numeric ranges for star rating displays
   - `total_price`: Calculates cart totals across multiple items
   - `total_items`: Counts items with different data structures
   - `multiply`: Performs multiplication in templates
   - `filter`, `urlencode`: Utilities for URL handling

13. **static/supplement_store/**  
   - **style.scss**: Main stylesheet with SCSS variables, mixins and responsive design rules
   - **style.css**: Compiled CSS from the SCSS source files with all styling rules
   - **style.css.map**: Source map file that connects the compiled CSS to the original SCSS
   - **images/**: Collection of product images, brand logos, UI elements and icons optimized for web display

14. **templates/supplement_store/**  
   HTML templates for the application:
   - **layout.html**: Base template containing the site structure, navigation, footer and common elements
   - **index.html**: Homepage template with featured products, categories and promotional content
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
   - **item.html**: Detailed product view with images, description and reviews
   - **error.html**: Custom error page for handling exceptions
   - **delivery_payment.html**: Shipping and payment information collection form
   - **confirmation_email.html**: Email template for order confirmations
   - **change_quantity_of_item.html**: Interface for updating cart quantities
   - **add_sale_to_item.html**: Admin interface for creating product discounts
   - **add_item_to_shop.html**: Admin form for adding new products to the store


### `supplements/` (Project Configuration)

1. **settings.py**  
   This is the main configuration module for the supplements Django project. Located at the root of project, it centralizes all environment-specific settings—API keys, database credentials, third-party integrations (reCAPTCHA, PayPal, Stripe, Django Allauth for social login), middleware, installed apps, email backends, session behavior and security settings. By leveraging django-environ to load secrets and flags from a .env file, it ensures that sensitive values (SECRET_KEY, database login, payment provider keys, etc.) remain out of source control.

2. **urls.py**  
   Primary URL configuration that defines the project's routing structure.

3. **wsgi.py** and **asgi.py**
   - WSGI configuration for traditional web servers (like Gunicorn)
   - ASGI configuration for asynchronous web servers
   - Both set up the necessary environment and application entry points for deployment

### `Additional Files`

1. **requirements.txt**  
   Project dependencies:
   - Django and extensions with specific versions
   - Database adapters and ORM extensions
   - AWS SDK for S3 integration
   - Payment processing libraries
   - Image processing libraries
   - Security packages

2. **.gitignore**  
   Version control exclusions to prevent sensitive and unnecessary files from being committed:
   - Environment files (.env) containing secret keys and credentials
   - Database files to avoid conflicts and security issues
   - Compiled Python files (*.pyc, __pycache__) to keep the repository clean
   - Media uploads and static file collections that should be generated on deployment
   - IDE-specific files and directories
   - Virtual environment folders

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

8. **Create a Superuser (for admin access, optional):**
    ```bash
    python manage.py createsuperuser
    ```

### Environment Configuration (.env)
Before running the application, create a .env file in your project's root directory (in the same folder where manage.py file is) and include the following variables. 

__Important__: Do not include spaces or quotation marks when adding values to the .env file.

```bash
# Django Secret Key
SECRET_KEY=

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

# Google reCAPTCHA
RECAPTCHA_PUBLIC_KEY=
RECAPTCHA_PRIVATE_KEY=

# Payment API Configuration
PAYPAL_RECEIVER_EMAIL=
PAYPAL_TEST=

# Stripe API Configuration
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
```

## Technologies Used

- **Backend**: Django, Python
- **Frontend**: JavaScript, SCSS, HTML
- **Database**: PostgreSQL
- **Authentication**: Django Auth, OAuth (Google, Facebook), Google reCAPTCHA
- **Payment Processing**: Stripe API, PayPal API
- **Hosting**: AWS (EC2, S3, RDS)