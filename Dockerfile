# Usamos una imagen de Python
FROM python:3.12

# Establecemos el directorio de trabajo en el contenedor
WORKDIR /app

# Copiamos el archivo requirements.txt e instalamos las dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiamos el resto de la app
COPY . .

# Exponemos el puerto 8000
EXPOSE 8000
# Comando por defecto para ejecutar el servidor de Django
CMD ["python", "princesse/manage.py", "runserver", "0.0.0.0:8000", "settings=settings.local"]