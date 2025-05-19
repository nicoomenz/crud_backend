from .base import *

from settings import PROJECT_NAME
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("MYSQL_DATABASE", "conico"),  # Nombre de la base de datos
        'USER': os.getenv("MYSQL_USER", "root"),        # Usuario de MySQL
        'PASSWORD': os.getenv("MYSQL_PASSWORD", "@Root1234"),  # Contraseña
        'HOST': os.getenv("DB_HOST", "localhost"),      # Host de la base de datos
        'PORT': os.getenv("DB_PORT", "3306"),           # Puerto de MySQL
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        },
    }
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.user.authentication.BearerTokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "princesse.altacostura@gmail.com"
EMAIL_HOST_PASSWORD = "rsjbkocjvlvqdigw"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
