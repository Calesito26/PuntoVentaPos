# Imagen oficial Python
FROM python:3.11-slim

# Evitar archivos pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Mostrar logs inmediatamente
ENV PYTHONUNBUFFERED=1

# Directorio trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar proyecto
COPY . .

# Puerto Django
EXPOSE 8000

# Comando inicio
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]