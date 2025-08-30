import environ
import os
from pathlib import Path

env = environ.Env(
    DEBUG=(bool, False)
)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

environ.Env.read_env(os.path.join(BASE_DIR, 'secrets.env'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

# ALLOWED_HOSTS = [x for x in env.list('ALLOWED_HOSTS')] #type:ignore

ALLOWED_HOSTS = ["*"]

AUTH_USER_MODEL = "listings.CustomUSer"

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #myapps
    'listings.apps.ListingsConfig',

    #third Party Apps
    'rest_framework',
    'corsheaders',
    'django_filters',
    'rest_framework_simplejwt',
    # 'django.contrib.staticfiles',
    'drf_yasg',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'alx_travel_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'alx_travel_app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'main':env.db_url('DB_PRO'),
    'default':env.db_url('DB_DEV')
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# THIRD PARTY APPS SETTINGS

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'EXCEPTION_HANDLER': 'utils.exceptionhandler.customexceptionhandler',
}

#swagger settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        # Basic Authentication
        'Basic': {
            'type': 'basic',  
        },
        # Bearer Token Authentication (JWT)
        'Bearer': {
            'type': 'apiKey',  
            'name': 'Authorization',  
            'in': 'header',  
            'description': 'JWT token for user authentication',  
        },
        # Token Authentication (DRF token authentication)
        'Token': {
            'type': 'apiKey', 
            'name': 'Authorization', 
            'in': 'header',  
            'description': 'Token for user authentication',  
        }
    },    
}


CORS_ALLOWED_ORIGINS = [x for x in env.list("CORS_ALLOWED_ORIGIN")] #type:ignore

CELERY_BROKER_URL = env('BROKER_URL')

if env("ENVIRONMENT").lower() == "PRODUCTION": #type:ignore
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') 
    SECURE_HSTS_PRELOAD = True  
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True  
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    X_FRAME_OPTIONS = 'DENY'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True


#CHAPPA_PAY API SETTINGS
PAYMENT_API_KEY=env('CHAPA_SECRET_KEY')
PAYMENT_API_BASE_URL=env('CHAPA_API_BASE_URL')
PAYMENT_VERIFY_URL=env('CHAPA_VERIFY_URL')
PAYMENT_CANCEL_URL=''
WEBHOOK_SECRET=env('WEBHOOK_SECRET_HASH')
WEBHOOK_URL=env('WEBHOOK_URL')

CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
]

# Use Django's SMTP backend
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Default "from" email address
DEFAULT_FROM_EMAIL = env('ADMIN_EMAIL')

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = env('ADMIN_EMAIL')
EMAIL_HOST_PASSWORD = env('ADMIN_SECRET_PASS')