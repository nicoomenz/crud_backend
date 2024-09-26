#!/bin/sh
set -e
cd ${PROJECT_NAME}

# Apply database migration
echo "===============Apply database migrations==============="
python3 manage.py makemigrations --settings=${DJANGO_SETTINGS_MODULE}
python3 manage.py makemigrations --settings=${DJANGO_SETTINGS_MODULE}
python3 manage.py migrate --settings=${DJANGO_SETTINGS_MODULE}


if [ ${RUN_LOAD_DATA} = "True" ]; then
    echo "===============Load User examples==============="
    python3 manage.py loaddata fixtures/*.json --settings=${DJANGO_SETTINGS_MODULE}
fi

# Collect static files
echo "===============Collect static files==============="
python3 manage.py collectstatic --noinput --settings=${DJANGO_SETTINGS_MODULE}

# Start server
echo "===============Starting server==============="
python3 manage.py runserver "0.0.0.0:8000" --settings=${DJANGO_SETTINGS_MODULE}

#!/bin/sh

# Espera a que la base de datos esté disponible
echo "Esperando a que la base de datos esté lista..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Base de datos lista."

# Aplica las migraciones
python princesse/manage.py migrate --settings=${"settings.local"}

# Inicia el servidor
exec "$@"