"""
https://docs.djangoproject.com/en/5.2/topics/settings/
https://docs.djangoproject.com/en/5.2/ref/settings/
"""
from pathlib import Path
from datetime import datetime as dt

APP_START_TIME = dt.now()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "89@j=*y-4n^^ee*%!xsbmqcsq-s49te4o%-(0=8@8=ixf!2jj("

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1','localhost']

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "rest_framework",
    "mpc_contracts"
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'COMPACT_JSON': True,
    'APPEND_SLASH': True,
}

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "mpc_core.urls"

WSGI_APPLICATION = "mpc_core.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR/"mpc_database/db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
