# Cinema Ticket API

API REST para sistema de compra de entradas de cine desarrollada con FastAPI y PostgreSQL.

## 🏗️ Arquitectura

- **Backend**: FastAPI (Python 3.12+)
- **Base de datos**: PostgreSQL + SQLAlchemy + Alembic + 
- **Autenticación**: JWT (JSON Web Tokens)
- **Almacenamiento de imágenes**: Cloudinary
- **Email**: SendGrid/SMTP
- **Contenedores**: Docker + Docker Compose

### Usar:

### 1. @asynccontextmanager con lifespan - Patrón moderno de FastAPI
- El mecanismo (@app.on_event) está deprecado
- Se recomienda usar el parámetro lifespan del objeto FastAPI, que funciona con un @asynccontextmanager.

### 2. **SQLAlchemy 2.0 moderno**
   - ✅ **Mejores tipos** - Sistema de tipos más robusto y expresivo
   - ⚡ **Mejor rendimiento** - Optimizaciones significativas en el ORM

### 3. **Type safety completa**
   - 🔍 **MyPy integration** - Verificación estática de tipos integrada

### 4. **Timezone aware**
   - 🌍 **Timestamps conscientes** - Manejo adecuado de zonas horarias
   - ⏰ **UTC por defecto** - Almacenamiento consistente en UTC

### 5. **Menos imports circulares**
   - 🏗️ **Base definido apropiadamente** - Estructura de imports optimizada
   - 🔄 **Organización clara** - Arquitectura sin dependencias circulares


## 📁 Estructura del Proyecto

```
.
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py
│   │           ├── movies.py
│   │           ├── purchases.py
│   │           └── admin.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── movie.py
│   │   └── purchase.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── movie.py
│   │   └── purchase.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── movie_service.py
│   │   ├── email_service.py
│   │   └── image_service.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── db/
│   ├── __init__.py
│   └── seed_script.py
├── migrations/
├── tests/
│   └── test_endpoints.py
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🗄️ Modelo de Base de Datos

### Tablas principales:

**users**

- id (PK)
- email (unique)
- phone
- first_name
- last_name
- password_hash
- role (admin/customer)
- is_active
- created_at

**movies**

- id (PK)
- title
- description
- genre
- duration
- rating
- price
- max_capacity
- available_tickets
- image_url
- is_active
- created_at

**purchases**

- id (PK)
- user_id (FK)
- movie_id (FK)
- quantity
- total_amount
- payment_info (JSON)
- status
- created_at

**tickets**

- id (PK)
- purchase_id (FK)
- ticket_code (unique)
- seat_number
- status

Editar `.env` con tus credenciales:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/cinema_db
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

SENDGRID_API_KEY=your-sendgrid-key
FROM_EMAIL=noreply@cinema.com
```

### 3. Instalación con Docker (Recomendado)

```bash
docker-compose up -d
```

### 4. Instalación Manual

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
alembic upgrade head

# Ejecutar seed data
python db/seed_script.py

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# o con
uvicorn app.main:app --reload
```

## 📋 Funcionalidades

### Módulos Implementados:

**1. Autenticación**

- Registro de usuarios
- Login con JWT
- Protección de rutas

**2. Gestión de Películas**

- CRUD completo de películas (Admin)
- Búsqueda y filtros públicos
- Subida de imágenes a Cloudinary

**3. Sistema de Compras**

- Compra de entradas (usuarios registrados)
- Generación de tickets únicos
- Confirmación por email

**4. Panel Administrativo**

- Gestión de clientes
- Consulta de compras
- Reportes básicos

## 🛠️ API Endpoints

#### Documentar todo con OpenAPI/Swagger

-  Router centralizado y esa implementación es estándar:
- Sobre el router pattern:
```
# api/v1/router.py
from fastapi import APIRouter
from .endpoints import auth, movies, purchases, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(movies.router, prefix="/movies", tags=["movies"]) 
api_router.include_router(purchases.router, prefix="/purchases", tags=["purchases"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
```
Los tags son importantes para la documentación automática de Swagger.

### Autenticación

**Requerimiento**: "Se debe realizar una funcionalidad que le permita a los clientes registrarse con su email, número de teléfono, nombre, apellido y contraseña"

```
POST /api/v1/auth/register         # Registro de clientes con datos completos
POST /api/v1/auth/login           # Login para clientes registrados
```

### Películas (Público)

**Requerimiento**: "Cualquier persona puede acceder a la aplicación para ver la información de las películas que hay disponibles. Hay la posibilidad de realizar una búsqueda de la película que se desea mediante filtros"

```
GET    /api/v1/movies              # Listar todas las películas activas (público)
GET    /api/v1/movies/search       # Búsqueda con filtros (género, precio, etc.)
GET    /api/v1/movies/{id}         # Detalle de película específica
GET    /api/v1/movies/{id}/availability # Tickets disponibles para la película
```

### Compras

**Requerimiento**: "El módulo de compras debe permitir la compra solo a usuarios registrados... debe permitir asignar la cantidad de tickets... debe permitir ingresar la información básica de pago"

```
POST /api/v1/purchases             # Realizar compra (solo usuarios autenticados)
GET  /api/v1/purchases             # Historial de compras del usuario actual
GET  /api/v1/purchases/{id}        # Detalle específico de una compra
```

### Administración de Películas

**Requerimiento**: "El módulo de administración debe permitir gestionar (Crear, Consultar, Modificar, Inhabilitar) las películas con su respectiva imagen"

```
POST   /api/v1/admin/movies            # Crear nueva película con imagen
PUT    /api/v1/admin/movies/{id}       # Modificar película existente
PATCH  /api/v1/admin/movies/{id}/toggle   # Inhabilitar/habilitar película
GET    /api/v1/admin/movies           # Consultar todas las películas (incluyendo inactivas)
```

### Consulta de Compras (Admin)

**Requerimiento**: "Debe existir una opción que permita consultar las compras realizadas de las películas de los clientes"

```
GET /api/v1/admin/purchases        # Todas las compras realizadas en el sistema
GET /api/v1/admin/purchases/movie/{movie_id} # Compras de una película específica
GET /api/v1/admin/purchases/user/{user_id}   # Compras de un cliente específico
GET /api/v1/admin/reports/sales    # Reporte consolidado de ventas
```
## 🔒️ Protección de rutas

### Rutas PÚBLICAS (sin JWT):

```
POST /api/v1/auth/register         # Registro público
POST /api/v1/auth/login           # Login público
GET  /api/v1/movies               # Ver películas (cualquier persona)
GET  /api/v1/movies/search        # Búsqueda pública con filtros
GET  /api/v1/movies/{id}          # Detalle de película
GET  /api/v1/movies/{id}/availability # Ver tickets disponibles
```

### Rutas PROTEGIDAS - Usuario autenticado:

```
POST /api/v1/purchases            # "Solo usuarios registrados"
GET  /api/v1/purchases            # Historial personal
GET  /api/v1/purchases/{id}       # Detalle de compra propia
```

### Rutas PROTEGIDAS - Solo Admin:

```
# Administración de películas
POST   /api/v1/admin/movies
PUT    /api/v1/admin/movies/{id}
PATCH  /api/v1/admin/movies/{id}/toggle
GET    /api/v1/admin/movies

# Administración de clientes
GET  /api/v1/admin/users
PATCH /api/v1/admin/users/{id}/toggle
GET  /api/v1/admin/users/{id}

# Consulta de compras
GET /api/v1/admin/purchases
GET /api/v1/admin/purchases/movie/{movie_id}
GET /api/v1/admin/purchases/user/{user_id}
GET /api/v1/admin/reports/sales
```

### Implementación de middleware:

- Middleware JWT para rutas /purchases/*
- Middleware JWT + role check para rutas /admin/*
- Sin middleware para rutas públicas de movies y auth

#### El assessment es claro: "El módulo de compras debe permitir la compra solo a usuarios registrados" y toda la administración es implícitamente para administradores.

## 🧪 Testing

```bash
# Ejecutar tests
pytest tests/

# Con coverage
pytest --cov=app tests/
```

## 📖 Documentación API

Una vez ejecutándose el servidor, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Configuración Pydantic v2

```
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
```

#### En Pydantic 2.x, el parámetro regex fue reemplazado por *pattern*

## 🐳 Docker

### Desarrollo

```bash
docker-compose up -d
```

### Producción

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📝 Seed Data

Para poblar la base de datos con datos de prueba:

```bash
python db/seed_script.py
```

Esto creará:

- Usuario admin (admin@cinema.com / admin123)
- Películas de ejemplo
- Usuarios de prueba

## 🔒 Seguridad

- Contraseñas hasheadas con bcrypt
- JWT tokens con expiración
- Validación de datos con Pydantic
- CORS configurado
- Rate limiting (opcional)

## 📊 Monitoreo

- Logs estructurados
- Health check endpoint: `/health`
- Métricas básicas de rendimiento