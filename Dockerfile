# Usamos una imagen de Python
FROM python:3.12
ENV PYTHONUNBUFFERED=1
# Establecemos el directorio de trabajo en el contenedor
WORKDIR /code/${PROJECT_NAME}

COPY docker-entrypoint.sh /code/${PROJECT_NAME}
COPY Pipfile* /code/${PROJECT_NAME}

RUN apt-get update && apt-get install -y --no-install-recommends git libmariadb-dev python3-dev gcc \
    jq unzip gcc libc-dev build-essential

RUN python -m pip install --upgrade pip pipenv
RUN pipenv lock
RUN pipenv install --dev --deploy --system

# RUN ["chmod", "+x", "docker-entrypoint.sh"]

# Copiamos el archivo requirements.txt e instalamos las dependencias
# COPY requirements.txt .
# RUN pip install -r requirements.txt

# Copiamos el resto de la app
# COPY . .

# Exponemos el puerto 8000
# EXPOSE 8000
# Comando por defecto para ejecutar el servidor de Django
# CMD ["python", "princesse/manage.py", "runserver", "0.0.0.0:8000", "settings=settings.local"]

