## 🛠️ API Endpoints

### Autenticación

**Requerimiento**: "Se debe realizar una funcionalidad que le permita a los clientes registrarse con su email, número de teléfono, nombre, apellido y contraseña"

```
POST /api/v1/auth/register         # Registro de clientes con datos completos
POST /api/v1/auth/login            # Login para clientes registrados
POST /api/v1/auth/logout           # 🔒 Logout con invalidación inmediata (BLACKLIST)
POST /api/v1/auth/logout-all       # 🔒 Cerrar todas las sesiones del usuario
GET  /api/v1/auth/me               # Información del usuario actual
GET  /api/v1/auth/verify-token     # Verificar validez del token (incluye verificación de blacklist)
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

### 🔒 Administración de Blacklist de Tokens (Admin)

**Funcionalidad avanzada**: Gestión completa de tokens invalidados para seguridad

```
GET    /api/v1/admin/blacklist/stats           # 📊 Estadísticas generales de la blacklist
GET    /api/v1/admin/blacklist/list            # 📋 Lista paginada de tokens invalidados
POST   /api/v1/admin/blacklist/cleanup         # 🧹 Limpiar tokens expirados automáticamente
POST   /api/v1/admin/users/{id}/logout-force   # ⚠️ Forzar logout de todas las sesiones de un usuario
DELETE /api/v1/admin/blacklist/{token_id}      # 🔓 Remover token específico de la blacklist (emergencia)
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
- Todas las rutas `/api/v1/auth/register` y `/api/v1/auth/login`
- Todas las rutas `/api/v1/movies/*`
- Todas las rutas `/api/v1/theaters/*`
- Todas las rutas `/api/v1/calendar/*`

### Rutas PROTEGIDAS - Usuario autenticado:
- `/api/v1/auth/logout` - Logout con blacklist
- `/api/v1/auth/logout-all` - Logout de todas las sesiones
- `/api/v1/auth/me` - Información del usuario
- `/api/v1/auth/verify-token` - Verificar token
- Todas las rutas `/api/v1/purchases/*`

### Rutas PROTEGIDAS - Solo Admin:
- Todas las rutas `/api/v1/admin/*` (incluyendo blacklist management)

---

## 🔒 Blacklist de Tokens - Detalles de Implementación

### Características de Seguridad:

- **Invalidación inmediata**: Los tokens se invalidan al momento del logout
- **Verificación en cada request**: Todos los endpoints protegidos verifican la blacklist
- **Auditoría completa**: Se registra quién, cuándo y por qué se invalidó cada token
- **Limpieza automática**: Tokens expirados se pueden eliminar periódicamente
- **Gestión administrativa**: Los admins pueden ver stats y forzar logout

### Casos de Uso:

- **Logout normal**: Usuario cierra sesión voluntariamente
- **Logout de emergencia**: Usuario sospecha que su cuenta fue comprometida
- **Acción administrativa**: Admin suspende usuario o detecta actividad sospechosa
- **Mantenimiento**: Limpieza periódica de tokens antiguos

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
- `page` - Número de página (para endpoints de blacklist)
- `page_size` - Tamaño de página (para endpoints de blacklist)

### Fechas:
- `start_date` / `end_date` - Formato: YYYY-MM-DD
- `date` - Fecha específica para programación

### Filtros de Blacklist (`/admin/blacklist/list`):
- `user_id` - Filtrar tokens por ID de usuario específico
- `reason` - Filtrar por razón de invalidación (logout, admin_action, etc.)

### Parámetros de Limpieza (`/admin/blacklist/cleanup`):
- `days_old` - Eliminar tokens más antiguos que X días (default: 30)

---

## 📊 Ejemplos de Respuestas de Blacklist

### Estadísticas de Blacklist:
```json
{
  "total_blacklisted_tokens": 157,
  "recent_blacklisted_24h": 23,
  "blacklist_reasons": [
    {"reason": "logout", "count": 134},
    {"reason": "admin_action", "count": 15},
    {"reason": "security_logout", "count": 8}
  ],
  "generated_at": "2024-09-03T15:30:00"
}
```

### Logout con Blacklist:
```json
{
  "message": "Sesión cerrada exitosamente. Token invalidado inmediatamente.",
  "user_id": 5,
  "logout_time": "2024-09-03T14:30:00"
}
```

### Logout Forzado por Admin:
```json
{
  "message": "Logout forzado aplicado al usuario Juan Pérez",
  "user_id": 5,
  "sessions_closed": 3,
  "reason": "security_breach",
  "admin_user": "Admin Cinema"
}
```

---

## 🎯 Niveles de Seguridad Implementados

1. **Básico**: Autenticación JWT estándar
2. **Intermedio**: Verificación de tokens activos vs inactivos
3. **Avanzado**: Blacklist de tokens con invalidación inmediata ✅
4. **Enterprise**: Auditoría completa y gestión administrativa ✅

Esta implementación coloca a Cinema Tickets API en el nivel **Enterprise** de seguridad de tokens.