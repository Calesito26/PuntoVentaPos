# PuntoVentaPOS

Sistema de punto de venta desarrollado con **Django** para la gestión de ventas, clientes, inventario, compras, gastos y usuarios.

## 🚀 Características principales

- Gestión de productos, inventario y ventas
- Registro y control de clientes
- Compras y proveedores
- Gastos del negocio
- Administración de usuarios y roles
- Exportación/importación de documentos (según módulos del proyecto)
- Interfaz web basada en Django Templates

## 📦 Requisitos

- Python 3.11+
- pip
- Git
- PostgreSQL (recomendado para ejecución local)
- Docker y Docker Compose (opcional, para entorno contenedor)

## 🔄 Clonar el proyecto

```bash
git clone https://github.com/Calesito26/PuntoVentaPos.git
cd PuntoVentaPos
```

## 🧰 Configuración del entorno

### Opción A: ejecutar con Docker (sin entorno virtual)

Este proyecto incluye `Dockerfile` y `docker-compose.yml`, por lo que puedes ejecutar todo con contenedores.

1. Clona el repositorio:

```bash
git clone https://github.com/Calesito26/PuntoVentaPos.git
cd PuntoVentaPos
```

2. Crea el archivo `.env` a partir de `.env.example`:

```bash
copy .env.example .env
```

o en Linux/macOS:

```bash
cp .env.example .env
```

3. Completa las variables del archivo `.env`:

```env
SECRET_KEY=clave-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=tu_base_de_datos
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_HOST=db
DB_PORT=5432
```

4. Levanta los contenedores:

```bash
docker compose up --build
```

5. Accede en:

- http://localhost:8000/

6. Para detenerlos:

```bash
docker compose down
```

### Opción B: ejecutar localmente (con entorno virtual)

1. Crea un entorno virtual:

```bash
python -m venv venv
```

2. Activa el entorno virtual:

- En Windows (PowerShell):

```powershell
venv\Scripts\activate
```

- En Windows (CMD):

```cmd
venv\Scripts\activate.bat
```

- En Linux/macOS:

```bash
source venv/bin/activate
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

4. Crea el archivo `.env` a partir de `.env.example`:

```bash
copy .env.example .env
```

o en Linux/macOS:

```bash
cp .env.example .env
```

5. Completa las variables del archivo `.env`:

```env
SECRET_KEY=clave-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=tu_base_de_datos
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

> El proyecto utiliza `python-decouple` y espera estas variables al iniciar Django.

## 🗄️ Base de datos

Si usas PostgreSQL local, crea la base de datos antes de aplicar migraciones.

Ejemplo:

```sql
CREATE DATABASE punto_venta_pos;
```

Luego aplica las migraciones:

```bash
python manage.py migrate
```

## 👤 Crear superusuario

```bash
python manage.py createsuperuser
```

## ▶️ Ejecutar el proyecto localmente

```bash
python manage.py runserver
```

Accede en:

- http://127.0.0.1:8000/

## 🔧 Flujo recomendado de trabajo

```bash
git status
git add .
git commit -m "Descripcion del cambio"
git push
```

## 📝 Notas importantes

- El archivo `.env` **no debe subirse al repositorio**.
- El repositorio ya incluye `.env.example` como ejemplo de configuración.
- Para nuevos ambientes, copia `.env.example` y completa las credenciales.

## 📂 Estructura principal

- `config/` → configuración global de Django
- `core/` → lógica base y utilidades del proyecto
- `usuarios/`, `productos/`, `ventas/`, `clientes/`, `inventario/`, `compras/`, `gastos/` → módulos del negocio
- `templates/` → plantillas HTML
- `manage.py` → ejecución de Django

## ✅ Flujo rápido de inicio

### Con Docker

```bash
git clone https://github.com/Calesito26/PuntoVentaPos.git
cd PuntoVentaPos
copy .env.example .env
# editar .env con tus credenciales
docker compose up --build
```

### Sin Docker

```bash
git clone https://github.com/Calesito26/PuntoVentaPos.git
cd PuntoVentaPos
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# editar .env con tus credenciales
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
