import os
from pathlib import Path
from django.db import models

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'some-secret-key'

INTERNAL_APPS = [
    "core",
    "account",
]

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.messages',
    # INSTALLED APPS
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'rest_framework_gis',
    'rest_access_policy',
    "corsheaders",
    "drf_standardized_errors",
    'generic_relations',
    'auditlog',
] + INTERNAL_APPS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

LANGUAGE_CODE = 'en-us'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'api_service.urls'

ADMIN_URL = "admin/"

SHOW_SWAGGER = False


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
            ],
        },
    },
]

DATALOOKUP_MODEL = "core.DataLookup"

AUTH_USER_MODEL = "account.User"

POLICIES_FILE_PATH = default=os.path.join(BASE_DIR, 'config', 'policies.json')
