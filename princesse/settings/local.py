from .base import *

from settings import PROJECT_NAME

import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'conico',  # Tu base de datos
        'USER': os.getenv("POSTGRES_USER", "root"),  # Asegúrate de que sea 'root'
        'PASSWORD': os.getenv("POSTGRES_PASSWORD", "conico"),  # Contraseña
        'HOST': os.getenv("DB_HOST", "db"),  # Debe ser 'db' (nombre del servicio en docker-compose)
        'PORT': os.getenv("DB_PORT", "5432"),
        'OPTIONS': {
            'options': '-c search_path=public'
        }
    }
}