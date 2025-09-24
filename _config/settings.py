import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.environ.get("DEBUG", "False") == "True" else False

ALLOWED_HOSTS = [os.environ.get("ALLOWED_HOST", "")]

if DEBUG:
    ALLOWED_HOSTS.extend(
        [
            "127.0.0.1",
            os.environ.get("PRIVATE_IP_ADDRESS", ""),
        ]
    )
    ABSOLUTE_URL = "http://127.0.0.1:8000"

else:
    ABSOLUTE_URL = f"https://{os.environ.get('ALLOWED_HOST', '')}"


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "account",
    "rules",
    "diary",
    "django_recaptcha",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "_config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "_config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("RDS_NAME"),
        "USER": os.environ.get("RDS_USER"),
        "PASSWORD": os.environ.get("RDS_PASSWORD"),
        "HOST": os.environ.get("RDS_HOST"),
        "PORT": os.environ.get("RDS_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "account.Accounts"


# https://docs.djangoproject.com/en/3.2/topics/security/

if DEBUG:
    CSRF_COOKIE_SECURE = False
else:
    # SECURE_SSL_REDIRECT = True - do not use it, it causes a redirection loop
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 60
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True  # For http protocol it has to be set to False
    CSRF_COOKIE_SECURE = True  # For http protocol it has to be set to False
    CSRF_TRUSTED_ORIGINS = []
    X_FRAME_OPTIONS = "DENY"

SESSION_COOKIE_AGE = 12 * 60 * 60


# E-mail
# https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-EMAIL_USE_TLS

EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
EMAIL_USE_TLS = True

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
MAILER_EMAIL_BACKEND = EMAIL_BACKEND
SERVER_EMAIL = EMAIL_HOST_USER


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Admin

ADMIN_ENABLED = True
ADMIN_NAME = os.environ.get("ADMIN_NAME")
ADMIN_EMAIL_ADDRESS = os.environ.get("ADMIN_EMAIL_ADDRESS")
if os.environ.get("EMAIL_LOGGING") == "True":
    ADMINS = [(ADMIN_NAME, ADMIN_EMAIL_ADDRESS)]


# Celery
# https://docs.celeryq.dev/en/stable/django

AMQP_PROTOCOL = os.environ.get("AMQP_PROTOCOL")
RABBITMQ_USERNAME = os.environ.get("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD")
RABBITMQ_BROKER_URL = os.environ.get("RABBITMQ_BROKER_URL")

CELERY_BROKER_URL = (
    f"{AMQP_PROTOCOL}://{RABBITMQ_USERNAME}:{RABBITMQ_PASSWORD}@{RABBITMQ_BROKER_URL}"
)
CELERY_RESULT_BACKEND = "rpc://"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TIMEZONE = "Europe/Warsaw"
CELERY_ENABLE_UTC = False


# reCAPTCHA

RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")

# Login URL

LOGIN_URL = "/sign-in"
LOGIN_REDIRECT_URL = "/sign-in"
