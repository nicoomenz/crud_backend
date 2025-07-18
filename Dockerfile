# Imagen base
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libpq-dev gcc git && \
    apt-get clean

# Copiar requirements
COPY requirements.txt /code/

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . /code/
