# Redis Cache

Redis actúa como capa de cache intermedia entre la API y la base de datos. 
En lugar de consultar la BD en cada request, la respuesta se guarda temporalmente en Redis. 
Las requests siguientes devuelven el dato cacheado sin tocar la BD.

```
Request → ¿Hay key en Redis?
              ├── SÍ (hit)  → Retorna datos del cache
              └── NO (miss) → Consulta la BD → Guarda en Redis → Retorna datos
```

---

## La key `home:8:4:4`

Cuando haces una request al endpoint home, el código genera una key con este formato:

```
home : {limit} : {page} : {theaters_count}
home :    8    :    4   :       4
```

El **value** es el JSON completo de la respuesta, con 3 secciones:

| Sección       | Contenido                        |
|---------------|----------------------------------|
| `cartelera`   | Películas actualmente en salas   |
| `coming_soon` | Próximos estrenos                |
| `presales`    | Películas en preventa            |

---

## TTL (tiempo de vida)

El TTL está configurado en **120 segundos** (2 minutos) en `app/core/config.py`:

```python
CACHE_HOME_TTL: int = 120
```

Cuando el TTL llega a 0, Redis borra la key automáticamente. La próxima request va a la BD, recalcula y vuelve a cachear desde cero.

Si en el dashboard ves `58s` restantes, simplemente significa que la key fue creada hace ~62 segundos — es normal.

---

## ¿Cómo se actualizan los datos?

Hay tres formas:

### 1. TTL (automático)
La key expira sola. Sin intervención, en máximo 120s los datos se refrescan.

### 2. Invalidación desde la API (automático)
Cuando se crea, edita o elimina una película vía los endpoints CRUD, el servicio invalida el cache automáticamente:

```python
# app/services/movie_service.py — líneas 58, 205, 219
cache.delete_pattern("home:*")
```

Esto borra todas las keys `home:*` al instante, forzando recarga desde la BD en la próxima request.

### 3. Manual desde el dashboard de Railway
1. Ir a la pestaña **Database → Data**
2. Buscar con `*` en el campo KEYS para ver todas las keys activas
3. Hacer clic en la key → icono de papelera para borrarla
4. La próxima request recarga desde la BD

### 4. Manual desde la terminal
```bash
# Ver todas las keys
redis-cli -u $REDIS_URL KEYS "*"

# Borrar una key específica
redis-cli -u $REDIS_URL DEL home:8:4:4

# Borrar todas las keys home
redis-cli -u $REDIS_URL KEYS "home:*" | xargs redis-cli -u $REDIS_URL DEL
```

---

## ¿Qué pasa si Redis no está disponible?

La app tiene modo **passthrough**: si Redis está caído o no configurado, todas las requests van directo a la BD sin error. El cache es transparente para el consumidor.

---

## Archivos relevantes

| Archivo | Rol |
|---|---|
| `app/core/cache.py` | Singleton `_CacheManager` — lógica de get/set/delete |
| `app/core/config.py` | `CACHE_HOME_TTL = 120` |
| `app/api/v1/endpoints/movies.py` | Genera la cache key y cachea la respuesta |
| `app/services/movie_service.py` | Invalida `home:*` en operaciones de escritura |

---

## Stats del dashboard (pestaña Stats)

| Métrica | Qué significa |
|---|---|
| **Hit Rate** | % de requests que usaron el cache (más alto = mejor) |
| **Hits** | Requests que encontraron la key en Redis |
| **Misses** | Requests que no encontraron la key (fueron a la BD) |
| **Expired Keys** | Keys que expiraron por TTL |
| **Total Keys** | Keys activas en este momento |
