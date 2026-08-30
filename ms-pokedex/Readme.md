# 🟡 POKÉDEX API — Manual del Proyecto

Backend de una Pokédex social: los usuarios se registran, descubren especies y arman equipos de hasta 6 Pokémon en slots ordenados. Proyecto de aprendizaje con prácticas de entorno real: arquitectura por features, capas, migraciones, Docker y autenticación JWT.

---

## 📚 Stack tecnológico

| Tecnología                          | Rol                                            |
| :---------------------------------- | :--------------------------------------------- |
| **FastAPI**                         | Framework web (endpoints, validación, OpenAPI) |
| **SQLAlchemy 2.0 (async)**          | ORM con `Mapped` / `mapped_column`             |
| **asyncpg**                         | Driver async de PostgreSQL                     |
| **PostgreSQL 16**                   | Base de datos (Docker)                         |
| **Pydantic v2 / pydantic-settings** | DTOs y configuración desde entorno             |
| **Alembic**                         | Migraciones de esquema                         |
| **bcrypt**                          | Hash de contraseñas                            |
| **PyJWT**                           | Tokens de autenticación                        |
| **Docker Compose**                  | Infraestructura local                          |
| **uv**                              | Gestor de dependencias                         |

---

## 🏗️ Arquitectura

### Organización por features

Cada capacidad del producto es un módulo independiente con sus propias capas:

```text
app/features/<feature>/
├── models.py       # Tablas (SQLAlchemy ORM)
├── schemas.py      # DTOs Pydantic (entrada/salida de la API)
├── repository.py   # Acceso a datos (SQL puro vía ORM)
├── service.py      # Reglas de negocio (SIN importar FastAPI)
└── router.py       # Controlador HTTP (endpoints)
```

Features actuales: `auth` (incluye `security.py` con bcrypt/JWT), `pokemon`, `teams`, `pokedex`.

### Viaje de una petición

```text
Cliente (JSON)
   │
   ▼
router.py      valida con schemas → traduce errores a códigos HTTP
   │
   ▼
service.py     aplica reglas de negocio (duplicados, permisos, slots)
   │
   ▼
repository.py  consultas SQLAlchemy (select 2.0, add/commit/refresh)
   │
   ▼
PostgreSQL     tablas definidas en models.py
```

### Convención de errores

| Excepción / caso                                    | Código HTTP |
| :-------------------------------------------------- | :---------: |
| Validación Pydantic fallida                         |     400     |
| Sin token o token inválido/expirado                 |     401     |
| Recurso de otro usuario                             |     403     |
| Recurso inexistente                                 |     404     |
| `ValueError` del service (duplicados, slot ocupado) |     409     |

---

## 📁 Estructura del repositorio

```text
PokeDex/
├── infra/
│   └── docker-compose.yml      # servicios api + db (PostgreSQL)
└── ms-pokedex/
    ├── alembic/
    │   ├── env.py              # configuración async de Alembic
    │   └── versions/           # migraciones (se versionan en git)
    ├── alembic.ini
    ├── app/
    │   ├── main.py             # app FastAPI, lifespan, routers, /health
    │   ├── core/
    │   │   ├── config.py       # Settings (env vars / .env)
    │   │   └── database.py     # Base, TimestampMixin, engine, get_db
    │   └── features/
    │       ├── auth/
    │       ├── pokemon/
    │       ├── teams/
    │       └── pokedex/
    ├── pyproject.toml
    ├── uv.lock                 # se commitea
    └── tests/
```

---

## 🚀 Levantar el proyecto desde cero

### Prerrequisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker (con el daemon corriendo)

### Pasos

```powershell
# 1. Dependencias
cd ms-pokedex
uv sync

# 2. Base de datos (desde la carpeta infra/)
cd ../infra
docker compose up -d db          # levanta solo PostgreSQL
cd ../ms-pokedex

# 3. Migraciones (Alembic es el dueño del esquema)
uv run alembic upgrade head

# 4. API en local
uv run uvicorn app.main:app --reload
```

Abrir **http://127.0.0.1:8000/docs** → Swagger UI con todos los endpoints.

> **Estrategia de desarrollo:** la infraestructura (DB) vive en Docker; la API corre en tu máquina con `--reload` para iterar rápido. `docker compose up -d` (todo) se usa para probar el conjunto completo, como en producción.

### Archivo `.env` (opcional)

Los defaults ya funcionan en local. Si quieres sobrescribirlos, crea `ms-pokedex/.env` (**nunca se commitea**):

```ini
DATABASE_URL=postgresql+asyncpg://pokedex:devpassword123@localhost:5432/pokedex
APP_ENV=development
SECRET_KEY=dev-secret-change-me
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## ⚙️ Configuración (`core/config.py`)

| Variable de entorno           | Campo                         | Default                      | Uso                  |
| :---------------------------- | :---------------------------- | :--------------------------- | :------------------- |
| `DATABASE_URL`                | `database_url`                | Postgres en `localhost:5432` | Conexión async       |
| `APP_ENV`                     | `app_env`                     | `development`                | Activa `echo` de SQL |
| `SECRET_KEY`                  | `secret_key`                  | `dev-secret-change-me`       | Firma del JWT        |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `access_token_expire_minutes` | `60`                         | Expiración del JWT   |

### ¿Cómo se leen las variables?

`settings = Settings()` se ejecuta **una sola vez, al importar el módulo** (arranque de la app). La prioridad es:

```text
Variable de entorno real  >  archivo .env  >  default de la clase
```

El matching es insensible a mayúsculas (`DATABASE_URL` → `database_url`) y pydantic convierte tipos (un `"120"` del entorno se vuelve `int 120`). En Docker, el compose inyecta `DATABASE_URL` con host `db` sin tocar el código.

---

## 🗄️ Base de datos y migraciones

**Alembic es el único dueño del esquema.** No hay `create_all` en la app: primero se migra, luego se arranca.

### Workflow al cambiar modelos

```powershell
uv run alembic revision --autogenerate -m "descripcion del cambio"
# ⚠️ SIEMPRE leer el archivo generado antes de aplicarlo
uv run alembic upgrade head
git add alembic/versions/ && git commit
```

### Reglas de oro

- Una migración **ya aplicada nunca se edita**: se crea una nueva que corrija.
- Las migraciones **se commitean** a git.
- `docker compose down -v` **borra el volumen `pgdata`** (todos los datos). Usar solo para resetear desarrollo.

---

## 🔌 Endpoints de la API

### auth (público / perfil)

| Método | Ruta             | Auth | Descripción                                         |
| :----- | :--------------- | :--: | :-------------------------------------------------- |
| POST   | `/auth/register` |  —   | Crea usuario (201). 409 si el email existe          |
| POST   | `/auth/login`    |  —   | Devuelve `{access_token, token_type}`. 401 si falla |
| GET    | `/users/me`      |  🔒  | Perfil del usuario autenticado                      |
| PATCH  | `/users/me`      |  🔒  | Actualiza nombre y/o contraseña                     |

### pokemon (catálogo base)

| Método               | Ruta                    | Descripción                         |
| :------------------- | :---------------------- | :---------------------------------- |
| GET                  | `/pokemon/`             | Lista paginada (`skip`, `limit`)    |
| POST                 | `/pokemon/`             | Crea especie (201). 409 duplicados  |
| GET / PATCH / DELETE | `/pokemon/{pokeapi_id}` | Detalle / edición parcial / borrado |

> El Pokémon se identifica públicamente por `pokeapi_id`; el `id` interno es privado de la DB.

### teams (🔒 todo protegido; escritura valida dueño → 403)

| Método         | Ruta                           | Descripción                                                               |
| :------------- | :----------------------------- | :------------------------------------------------------------------------ |
| GET            | `/teams/`                      | Equipos del usuario                                                       |
| POST           | `/teams/`                      | Crea equipo (201). 409 nombre duplicado                                   |
| GET            | `/teams/{id}`                  | Detalle con su alineación (`TeamDetail`)                                  |
| PATCH / DELETE | `/teams/{id}`                  | Edición parcial / borrado (204)                                           |
| POST           | `/teams/{id}/pokemons`         | Agrega especie a un slot (201). 404 especie inexistente, 409 slot ocupado |
| PATCH / DELETE | `/teams/{id}/pokemons/{tp_id}` | Mueve de slot / quita del equipo                                          |

### pokedex (🔒)

| Método | Ruta        | Descripción                             |
| :----- | :---------- | :-------------------------------------- |
| GET    | `/pokedex/` | Especies descubiertas por el usuario    |
| POST   | `/pokedex/` | Registro manual (201). 409 si ya estaba |

### sistema

| Método | Ruta      | Descripción                     |
| :----- | :-------- | :------------------------------ |
| GET    | `/health` | Healthcheck (lo usa el compose) |

### Ejemplos de cuerpos JSON

**Registro** → `POST /auth/register`

```json
{ "name": "Ash Ketchum", "email": "ash@pokedex.dev", "password": "Pikachu123!" }
```

**Agregar Pokémon a equipo** → `POST /teams/{id}/pokemons`

```json
{ "pokeapi_id": 25, "slot": 1 }
```

**Equipo con alineación** → `GET /teams/{id}`

```json
{
  "id": 1,
  "name": "Equipo Kanto",
  "description": "Mi equipo principal",
  "user_id": 1,
  "pokemons": [
    {
      "id": 101,
      "team_id": 1,
      "pokeapi_id": 25,
      "name": "pikachu",
      "photo_url": "https://.../25.png",
      "slot": 1,
      "created_at": "2026-08-30T10:25:00Z"
    }
  ],
  "created_at": "2026-08-30T10:20:00Z",
  "updated_at": "2026-08-30T10:20:00Z"
}
```

### Probar con Swagger

1. `POST /auth/register` y `POST /auth/login`.
2. Copiar el `access_token` → botón **Authorize** → pegar el token.
3. Operar sobre teams/pokedex con el 🔓 activado.

---

## 🧠 Decisiones de diseño (resumen de ADRs)

1. **Claves subrogadas + identidad pública**: todas las tablas tienen `id` propio; Pokémon se expone por `pokeapi_id`. La identidad interna es estable y las FKs no dependen de sistemas externos.
2. **`slot` en vez de `order`**: `ORDER` es palabra reservada de SQL.
3. **TeamPokemon permite especies repetidas** en distinto slot; `UNIQUE(team_id, slot)` garantiza posiciones únicas. PK con `id` propio para operar instancias.
4. **Pokedex = catálogo de especies**: `UNIQUE(user_id, pokemon_id)`; se auto-registra al agregar un Pokémon a un equipo (regla cruzada aplicada en `TeamService`).
5. **Services sin FastAPI**: lanzan `ValueError`/`PermissionError`; los routers traducen a HTTP. Mismo service serviría para un CLI o un worker.
6. **Hashing en el service, no en el repository**: el repository nunca ve contraseñas en texto plano.
7. **Login con mensaje genérico** ("Credenciales inválidas") para evitar enumeración de usuarios.
8. **Timestamps con `server_default=func.now()`**: las fechas las genera PostgreSQL; `onupdate` mantiene `updated_at`.
9. **Cascadas `ondelete=CASCADE`** en FKs hijas: borrar usuario/equipo/Pokémon limpia sus relaciones.
10. **Config por entorno**: el mismo código corre en local y en Docker; el entorno gana sobre el `.env` y el `.env` sobre el default.

---

## 🧪 Pruebas

- Manuales vía Swagger (flujo completo: register → login → Authorize → crear Pokémon → crear team → agregar al team → ver `TeamDetail` → ver Pokédex auto-registrada).
- Tests automatizados: pendientes de cobertura >80% (DoD del roadmap).

---

## 🗺️ Próximos pasos (roadmap)

- **Sprint 2**: cliente PokeAPI + caché Redis (Cache-Aside, TTL 5 min) + rate limiting; al agregar especies que no existen localmente, se traerán de PokeAPI automáticamente.
- **Sprint 3**: frontend React/Vite consumiendo esta API.
- **Sprint 4**: hardening, excepciones personalizadas, seeds, ADRs formales y documentación final.
