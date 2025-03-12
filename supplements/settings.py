"""
Django settings for supplements project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
import environ
import dj_database_url
import django_heroku

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")
if not SECRET_KEY:
    raise Exception("The SECRET_KEY setting must not be empty.")
RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['vitality-vault-048b9a26d0f5.herokuapp.com']

# Application definition

SITE_ID=2

INSTALLED_APPS = [
    'supplement_store',
    'django_recaptcha',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cleanup.apps.CleanupConfig',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'paypal.standard.ipn',
    # 'django_crontab', kada se postavi na server
]

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email"
        ],
        "AUTH_PARAMS": {"access_type": "online"}
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
        ],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': 'path.to.callable',
        'VERIFIED_EMAIL': True,
        'VERSION': 'v13.0',
        'GRAPH_API_URL': 'https://graph.facebook.com/v13.0',
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'supplements.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'supplement_store.context_processors.give_items',
            ],
        },
    },
]

WSGI_APPLICATION = 'supplements.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': env('DB_NAME'),
    #     'USER': env('DB_USER'),
    #     'PASSWORD': env('DB_PASSWORD'),
    #     'HOST': env('DB_HOST'),
    #     'PORT': env('DB_PORT'),
    # },
    'default': dj_database_url.config(default=env('DATABASE_URL'))
}

# Email configuration 

EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT')
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL')
EMAIL_FROM = env('EMAIL_FROM')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

EMAIL_LOG_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_TIMEOUT = 30


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_USER_MODEL = 'supplement_store.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'supplement_store', 'static'),
]
django_heroku.settings(locals())

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REDIRECT_FIELD_NAME = '/login'
LOGIN_URL = '/login'

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend"
)

SOCIALACCOUNT_LOGIN_ON_GET = True
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

PAYPAL_RECEIVER_EMAIL = env('PAYPAL_RECEIVER_EMAIL')
PAYPAL_TEST = env('PAYPAL_TEST')

STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')

SESSION_COOKIE_AGE = 60 * 60 * 24 * 28
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True



# kada se postavi na server
# CRONJOBS = [
#     ('0 0 * * *', 'django.core.management.call_command', ['update_items_status']),
# ]
# python manage.py crontab add
# python manage.py crontab show