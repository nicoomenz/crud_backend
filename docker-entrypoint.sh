#!/bin/sh
set -e

echo "Applying database migrations..."
python princesse/manage.py makemigrations --settings=settings.local
python princesse/manage.py migrate --settings=settings.local

# Inicia el servidor
exec "$@"