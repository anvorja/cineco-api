## 🛠️ API Endpoints

### Autenticación

**Requerimiento**: "Se debe realizar una funcionalidad que le permita a los clientes registrarse con su email, número de teléfono, nombre, apellido y contraseña"

```
POST /api/v1/auth/register         # Registro de clientes con datos completos
POST /api/v1/auth/login            # Login para clientes registrados
GET  /api/v1/auth/me               # Información del usuario actual
GET  /api/v1/auth/verify-token     # Verificar validez del token
```

### Películas (Público)

**Requerimiento**: "Cualquier persona puede acceder a la aplicación para ver la información de las películas que hay disponibles. Hay la posibilidad de realizar una búsqueda de la película que se desea mediante filtros"

```
GET    /api/v1/movies                    # Listar todas las películas activas (público)
GET    /api/v1/movies/search             # Búsqueda con filtros (género, precio, etc.)
GET    /api/v1/movies/coming-soon        # Próximos estrenos
GET    /api/v1/movies/presales           # Películas en preventa
GET    /api/v1/movies/{id}               # Detalle de película específica
GET    /api/v1/movies/{id}/showtimes     # Horarios de la película
GET    /api/v1/movies/{id}/theaters      # Teatros donde se proyecta
GET    /api/v1/movies/{id}/availability  # Información completa de disponibilidad
```

### Teatros (Público)

**Funcionalidad adicional**: Gestión completa de teatros y programación

```
GET    /api/v1/theaters                  # Listar todos los teatros activos
GET    /api/v1/theaters/{id}             # Información detallada del teatro
GET    /api/v1/theaters/{id}/movies      # Películas que se proyectan en el teatro
GET    /api/v1/theaters/{id}/schedule    # Programación del teatro por fecha
```

### Compras

**Requerimiento**: "El módulo de compras debe permitir la compra solo a usuarios registrados... debe permitir asignar la cantidad de tickets... debe permitir ingresar la información básica de pago"

```
POST /api/v1/purchases                   # Realizar compra (solo usuarios autenticados)
GET  /api/v1/purchases                   # Historial de compras del usuario actual
GET  /api/v1/purchases/{id}              # Detalle específico de una compra
```

### Administración de Películas

**Requerimiento**: "El módulo de administración debe permitir gestionar (Crear, Consultar, Modificar, Inhabilitar) las películas con su respectiva imagen"

```
POST   /api/v1/admin/movies                    # Crear nueva película
GET    /api/v1/admin/movies                    # Consultar todas las películas (incluyendo inactivas)
GET    /api/v1/admin/movies/{id}               # Obtener película por ID (incluyendo inactivas)
PUT    /api/v1/admin/movies/{id}               # Modificar película existente
PATCH  /api/v1/admin/movies/{id}/toggle        # Inhabilitar/habilitar película
POST   /api/v1/admin/movies/{id}/showtimes     # Crear horarios para película específica
```

### Administración de Teatros (Admin)

**Funcionalidad adicional**: Gestión completa de teatros

```
POST   /api/v1/admin/theaters               # Crear nuevo teatro
GET    /api/v1/admin/theaters               # Consultar todos los teatros (incluyendo inactivos)
```

### Gestión de Usuarios (Admin)

```
GET    /api/v1/admin/users                 # Listar todos los usuarios
GET    /api/v1/admin/users/{id}            # Información detallada del usuario
PATCH  /api/v1/admin/users/{id}/toggle     # Activar/desactivar usuario
```

### Consulta de Compras (Admin)

**Requerimiento**: "Debe existir una opción que permita consultar las compras realizadas de las películas de los clientes"

```
GET /api/v1/admin/purchases                # Todas las compras realizadas en el sistema
GET /api/v1/admin/purchases/movie/{id}     # Compras de una película específica
GET /api/v1/admin/purchases/user/{id}      # Compras de un cliente específico
GET /api/v1/admin/reports/sales            # Reporte consolidado de ventas
```

### Calendario y Programación

**Funcionalidad adicional**: Vista de programación como cines reales

```
GET /api/v1/calendar/week                    # Calendario semanal de programación
GET /api/v1/calendar/theater/{name}          # Programación específica de un teatro
GET /api/v1/calendar/movie/{id}/schedule     # Horarios de película en todos los teatros
```

---

## 🔒 Protección de Rutas

### Rutas PÚBLICAS (sin JWT):
- Todas las rutas `/api/v1/auth/*` 
- Todas las rutas `/api/v1/movies/*`
- Todas las rutas `/api/v1/theaters/*`
- Todas las rutas `/api/v1/calendar/*`

### Rutas PROTEGIDAS - Usuario autenticado:
- Todas las rutas `/api/v1/purchases/*`

### Rutas PROTEGIDAS - Solo Admin:
- Todas las rutas `/api/v1/admin/*`

---

## 📋 Parámetros de Query Comunes

### Filtros de Búsqueda (`/movies/search`):
- `q` - Búsqueda en título, descripción y director
- `genre` - Filtrar por género
- `director` - Filtrar por director  
- `country` - Filtrar por país
- `min_price` / `max_price` - Rango de precios
- `rating` - Clasificación (G, PG, PG-13, R, NC-17)
- `status` - Estado (in_theaters, coming_soon, ended)
- `theater` - Filtrar por teatro
- `available_only` - Solo con tickets disponibles

### Paginación:
- `skip` - Registros a omitir (default: 0)
- `limit` - Máximo registros (default: 10-20 según endpoint)

### Fechas:
- `start_date` / `end_date` - Formato: YYYY-MM-DD
- `date` - Fecha específica para programación