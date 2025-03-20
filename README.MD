# Vitality Vault

Vitality Vault is an e-commerce web store built as the final project for Harvard's CS50W course. This project allows users to browse and purchase supplements online with a user-friendly interface. The application is developed using Python (with Django) on the back end and JavaScript and SCSS on the front end.  
Vitality Vault is hosted on AWS.  
The link for the website: [vitality-vault.live](https://vitality-vault.live)

## 🧐 Distinctiveness and Complexity

This project integrates a full-stack solution with Django, featuring user authentication, dynamic product listings, a shopping cart mechanism, and an admin interface. It handles database management, third-party API integrations (for payments and email), and secure user interactions.

Rather than being a static site, Vitality Vault is a functional e-commerce application with complex business logic, secure authentication, and multi-layered configuration. The project demonstrates robust coordination between back-end processes (views, models, and migrations) and front-end design (templates and SCSS styling), fulfilling the distinctiveness and complexity requirements.

## 🚀 Unique Features

Vitality Vault introduces several features that extend beyond the scope of the CS50W Project 2 (Commerce):

- **Advanced Search and Filtering:** Users can search for supplements based on various criteria such as brand, category and flavor, enabling a more personalized shopping experience.

- **User Reviews and Ratings:** Implements a system where customers can leave reviews and rate products, fostering a community-driven platform and aiding new customers in making informed decisions.

- **Comprehensive Customer Support System:** Implements a customer support system.

- **Social Media Authentication:** Allows users to register and log in using their Google or Facebook accounts, streamlining the authentication process and enhancing user convenience.

- **Enhanced Security with reCAPTCHA:** Integrates Google reCAPTCHA to protect the platform from spam and abuse, ensuring that interactions are performed by real users.

- **Multiple Payment Gateways:** Supports both PayPal and Stripe for payment processing, offering users flexibility in choosing their preferred payment method and ensuring secure transactions.


These features demonstrate the additional complexity and functionality of Vitality Vault, distinguishing it from the foundational e-commerce structure of Project 2.

## 🗃️ File Structure and Contents

Below is an overview of the key files and directories:

### 📂 `supplement_store/`

The `supplement_store/` folder contains the main Django application code responsible for managing the e-commerce functionality of the Vitality Vault project. Below is a breakdown of each file and folder in this directory:

1. **admin.py**  
   Registers the models from the supplement_store app with Django’s admin interface. Configures how the supplement-related models are displayed and managed in the admin panel.

2. **apps.py**  
   Configures the supplement_store application and ensures that signal handlers are connected when the application is ready.

3. **context_processors.py**  
   Defines a custom context processor that enriches the template context with commonly needed data, such as cart items, wishlist items, brand and category lists, and available countries.

4. **countries.py**  
   Defines a dictionary mapping country codes to their corresponding localized country names, used to populate country selection options in forms.

5. **forms.py**  
   Contains Django form classes used for handling user input related to supplements (e.g., registration forms, item or order forms). Simplifies data validation and rendering in templates.

6. **models.py**  
   Defines the data models for the supplement store. Represents the database schema for users, items, orders, and other relevant entities, crucial for data persistence.

7. **shop_utils.py**  
   Provides utility functions that assist in processing data for the e-commerce store. Used in views to handle filtering, sorting, image processing, and merging session-based cart or wishlist data with the database.

8. **signals.py**  
   Contains signal handlers that perform specific actions in response to certain signals.

9. **urls.py**  
   Maps URL patterns to the corresponding view functions within the supplement_store app. Essential for routing incoming requests to the appropriate views based on URL paths.

10. **views.py**  
    Contains view functions or class-based views that handle HTTP requests and responses. Defines logic for rendering product listings, product details, shopping cart interactions, and checkout processes.

11. **management/commands/update_items_status.py**  
    A Django management command that updates the status of items in the store. Designed to run periodically (e.g., via a cron job) to keep item attributes up to date.

12. **templatetags/custom_filters.py**  
    Defines custom template filters to extend the functionality of the default Django template system by providing reusable utility filters.

13. **static/supplement_store/**  
    Contains static assets (CSS, SCSS, JavaScript, images) related to the supplement_store application. Organizes all the resources needed for styling and front-end interactivity.

14. **templates/supplement_store/**  
    Houses HTML templates specific to the supplement_store app. These templates render the front-end views for product pages, shopping cart, and other user interfaces.

### 📂 `supplements/`

1. **settings.py**  
   Configures the global settings for Vitality Vault. Sets up environment variables, database connections, installed applications, middleware, and static files. Uses the `environ` package to load sensitive values (e.g., `SECRET_KEY`, reCAPTCHA keys, database credentials, email settings) from a `.env` file. More details are provided in the [Environment Configuration](#environment-configuration-env) section.

2. **urls.py**  
   Defines the root URL configuration for the project. Maps URL patterns to view functions and includes URL configurations from installed apps to ensure proper request routing.

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

### Environment Configuration (.env)
Before running the application, create a .env file in your project’s root directory and include the following variables. These settings configure critical aspects of the application such as security keys, database connections, email service, and payment gateways.

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