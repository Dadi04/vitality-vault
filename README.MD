# Vitality Vault

Vitality Vault is an e-commerce web store built as the final project for Harvard's CS50W course. This project allows users to browse and purchase supplements online with a user-friendly interface. The application is developed using Python (with Django) on the back end and JavaScript and SCSS on the front end.  
Vitality Vault is hosted on AWS.  
The link for the website: [vitality-vault.live](https://vitality-vault.live)

## 🧐 Distinctiveness and Complexity

Unlike Project 2 (Commerce), which was a basic auction platform with limited functionality, Vitality Vault is a comprehensive e-commerce solution that incorporates advanced features and complex integrations typical of modern web applications.

### Distinctiveness from Project 2 (Commerce)

1. **Authentication System**: While Project 2 utilized basic Django authentication, Vitality Vault implements a sophisticated authentication system that includes:
   - Social media integration allowing users to authenticate via Google and Facebook
   - Password reset functionality with email verification
   - Enhanced security with Google reCAPTCHA integration to prevent automated bot attacks
   - Custom user profiles with order history, saved payment methods, and shipping addresses

2. **Payment Processing**: Project 2 had no real payment processing, but Vitality Vault integrates:
   - Multiple payment gateways (PayPal and Stripe) with full checkout flows
   - Secure handling of payment information
   - Order confirmation and invoice generation
   - Automated email notifications for order status changes

3. **Advanced Product Management**: Unlike Project 2's simple item listings, Vitality Vault features:
   - Complex product variants (flavors, sizes, packaging options)
   - Dynamic inventory management with automated status updates
   - Product categorization with hierarchical navigation
   - Related product recommendations

### Technical Complexity

1. **Front-end Development**: I implemented extensive JavaScript functionality for:
   - Asynchronous cart and wishlist updates without page reloads
   - Dynamic filtering and sorting of product listings
   - Interactive product image galleries with zoom functionality
   - Responsive design with custom breakpoints for mobile, tablet, and desktop views
   - Client-side form validation before submission

2. **Back-end Architecture**: I developed a sophisticated Django application with:
   - Custom middleware for handling user sessions and authentication
   - Complex database models with multiple foreign key relationships
   - Signal handlers for automated processing when models are updated
   - Custom Django management commands for scheduled tasks
   - Context processors for global template data availability

3. **Database Design**: I designed a normalized database schema with:
   - Over 10 interconnected models managing product information, user data, orders, and reviews
   - Custom model methods for business logic
   - Efficient query optimization using select_related and prefetch_related
   - Database migrations for schema evolution

4. **Third-party API Integration**: I integrated multiple external services:
   - Payment processing APIs (Stripe and PayPal)
   - Email delivery services
   - Social authentication providers
   - Google reCAPTCHA

5. **Deployment and DevOps**: I implemented:
   - AWS deployment with proper security configurations
   - Static and media file handling with S3
   - Environment-specific settings management
   - Secure handling of sensitive information using environment variables

These elements demonstrate that Vitality Vault goes far beyond a basic e-commerce site, incorporating complex business logic, sophisticated user interactions, and professional-grade security measures that exceed the requirements of Project 2.

## 🚀 Unique Features

Vitality Vault introduces several features that extend beyond the scope of the CS50W Project 2 (Commerce):

- **Advanced Search and Filtering:** Users can search for supplements based on various criteria such as brand, category and flavor, enabling a more personalized shopping experience.

- **User Reviews and Ratings:** Implements a system where customers can leave reviews and rate products, fostering a community-driven platform and aiding new customers in making informed decisions.

- **Comprehensive Customer Support System:** Implements a customer support system.

- **Social Media Authentication:** Allows users to register and log in using their Google or Facebook accounts, streamlining the authentication process and enhancing user convenience.

- **Enhanced Security with reCAPTCHA:** Integrates Google reCAPTCHA to protect the platform from spam and abuse, ensuring that interactions are performed by real users.

- **Multiple Payment Gateways:** Supports both PayPal and Stripe for payment processing, offering users flexibility in choosing their preferred payment method and ensuring secure transactions.


These features demonstrate the additional complexity and functionality of Vitality Vault, distinguishing it from the foundational e-commerce structure of Project 2.

## 🗃️ Files Created and Their Contents

Below is a detailed explanation of all the files I created for this project and what they contain:

### 📂 `supplement_store/`

1. **models.py**  
   I designed and implemented the database schema for the entire application, including:
   - `User` model that extends Django's AbstractUser, adding fields for phone numbers, addresses, and user preferences
   - `Item` model with comprehensive product information, including name, description, price, inventory status, and image fields
   - `Category` and `Brand` models for product organization with many-to-many relationships
   - `Order` and `OrderItem` models that track customer purchases with status progression
   - `Review` model for user feedback with star ratings and moderation flags
   - `Wishlist` model to store items users want to save for later
   - `Address` model with validation for shipping and billing information
   - Custom model methods for calculating discounts, checking availability, and managing stock levels

2. **views.py**  
   I wrote all view functions and class-based views handling the application's core functionality:
   - Product listing views with pagination and complex filtering
   - Shopping cart views with AJAX functionality for adding/removing items
   - User authentication views including social login integration
   - Order processing views managing the checkout pipeline
   - Review submission and moderation views
   - User profile management views with order history
   - API views providing JSON responses for frontend interactivity
   - Search functionality with multiple filter criteria

3. **forms.py**  
   I created all form classes to handle user input throughout the site:
   - User registration form with custom validation and reCAPTCHA integration
   - Profile editing form with multiple address fields
   - Product review form with star rating widget
   - Advanced search form with multiple filter options
   - Checkout forms for shipping and payment information
   - Contact form with email validation
   - Admin forms for product management

4. **admin.py**  
   I customized the Django admin interface for efficient store management:
   - Custom ModelAdmin classes with list displays and filters
   - Inline editing capabilities for related models
   - Custom admin actions for batch processing (e.g., marking items as featured)
   - Search fields and list filters for each model
   - Admin form customization with widgets and help text
   - Permission restrictions for different admin user roles

5. **urls.py**  
   I designed the URL structure for the entire application:
   - RESTful URL patterns for all resources
   - Namespaced URL patterns for organization
   - AJAX endpoints for dynamic content updates
   - Authentication URLs including social auth callbacks
   - Admin URLs with custom views
   - Sitemap and robots.txt URL configurations

6. **shop_utils.py**  
   I developed utility functions that power various features:
   - Cart calculation functions for subtotals, taxes, and shipping
   - Image processing utilities for product uploads
   - Session-database merging for anonymous to logged-in user transitions
   - Search and filtering algorithms
   - Recommendation engine based on purchase history
   - Security utilities for order verification
   - Email formatting and sending functions

7. **context_processors.py**  
   I wrote custom context processors to make data available across templates:
   - Cart information accessible on all pages
   - User wishlist data
   - Category and brand navigation hierarchies
   - Site-wide notifications
   - Currency and region information
   - Recently viewed products

8. **signals.py**  
   I implemented Django signals to automate processes:
   - Post-save signal for order confirmation emails
   - User registration signals for welcome emails
   - Inventory update signals when orders are placed
   - Review moderation signals for admin notifications
   - Custom signal handlers for third-party integrations

9. **middleware.py**  
   I created custom middleware components:
   - Shopping cart middleware for session management
   - Region detection middleware for localized pricing
   - Performance monitoring middleware
   - Security headers middleware
   - Referral tracking middleware

10. **apps.py**  
    I configured the application with:
    - Signal connection setup
    - App configuration settings
    - App-specific settings initialization
    - Plugin registration

11. **countries.py**  
    I developed this utility file containing:
    - Comprehensive country code mappings for address forms
    - Region groupings for shipping calculations
    - Country-specific validation rules
    - Currency mappings by country

12. **management/commands/update_items_status.py**  
    I created this custom management command to:
    - Automatically update product availability based on inventory
    - Flag low-stock items
    - Update featured product rotations
    - Generate inventory reports
    - Send notifications for out-of-stock items

13. **templatetags/custom_filters.py**  
    I implemented custom template filters and tags:
    - Currency formatting with proper symbols
    - Date formatting for orders and reviews
    - Star rating rendering
    - Text truncation with HTML awareness
    - URL generation with query parameters
    - Image processing tags

14. **static/supplement_store/**  
    I designed and developed all frontend assets:
    - **style.scss**: Main stylesheet with SCSS variables, mixins and responsive design rules
    - **style.css**: Compiled CSS from the SCSS source files with all styling rules
    - **style.css.map**: Source map file that connects the compiled CSS to the original SCSS for debugging
    - **images/**: Collection of product images, brand logos, UI elements, and icons optimized for web display

15. **templates/supplement_store/**  
    I created all HTML templates for the application:
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


### 📂 `supplements/` (Project Configuration)

1. **settings.py**  
   I configured all Django settings for the project:
   - Environment-specific configurations (development, production)
   - Security settings including CSRF protection and secure cookies
   - Database configuration with connection pooling
   - Static and media file handling with AWS S3 integration
   - Third-party app settings (Stripe, PayPal, reCAPTCHA)
   - Caching configuration with Redis
   - Logging setup with rotation and monitoring
   - Custom middleware configuration
   - Email backend configuration

2. **urls.py**  
   I created the root URL configuration:
   - Main app URL includes with appropriate namespaces
   - Admin URL customization
   - Static and media URL handlers for development
   - Error page handlers (404, 500)
   - Health check endpoints for monitoring
   - Documentation URLs

3. **wsgi.py** and **asgi.py**  
   I configured the WSGI and ASGI applications:
   - Production server interface setup
   - Environment configuration loading
   - Path configurations
   - Application initialization

### 📂 `Additional Files`

1. **requirements.txt**  
   I carefully selected and maintained all project dependencies:
   - Django and extensions with specific versions
   - Database adapters and ORM extensions
   - AWS SDK for S3 integration
   - Payment processing libraries
   - Image processing libraries
   - Security packages
   - Performance optimization tools

2. **.gitignore**  
   I configured version control exclusions to prevent sensitive and unnecessary files from being committed:
   - Environment files (.env) containing secret keys and credentials
   - Database files to avoid conflicts and security issues
   - Compiled Python files (*.pyc, __pycache__) to keep the repository clean
   - Media uploads and static file collections that should be generated on deployment
   - IDE-specific files and directories
   - Virtual environment folders

3. **manage.py**  
   I configured the Django management script:
   - Environment setup code
   - Custom command-line arguments
   - Project path configuration

Each file was carefully crafted to fulfill specific requirements of the application while maintaining clean code practices, proper documentation, and security best practices.

## 🛠️ Installation

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

## 💻 Technologies Used

- **Backend**: Django 4.2, Python 3.10
- **Frontend**: JavaScript (ES6+), SCSS, HTML5
- **Database**: PostgreSQL
- **Authentication**: Django Auth, OAuth (Google, Facebook)
- **Payment Processing**: Stripe API, PayPal API
- **Deployment**: AWS (EC2, S3, RDS)

## 🔒 Security Features

- Cross-Site Request Forgery (CSRF) protection
- SQL injection prevention through Django's ORM
- Password hashing with PBKDF2
- Google reCAPTCHA for form submissions
- HTTPS enforcement
- Secure cookie handling
- Input validation and sanitization

## 🔄 Project Evolution

Throughout the development process, I continuously improved the application based on user feedback and testing:

1. Initially, I started with a basic product listing and cart functionality
2. Added user authentication and profile management
3. Implemented payment processing with Stripe
4. Added PayPal as an alternative payment method
5. Integrated social login options
6. Enhanced the UI with responsive design improvements
7. Added the review and rating system
8. Implemented advanced search and filtering
9. Added performance optimizations for database queries and page loading

Each iteration involved both frontend and backend changes, requiring me to coordinate the development efforts across the stack.