# API de productos y categorías (MVC + PostgreSQL)

Proyecto de ejemplo con un CRUD de **categorías** y **productos**. Una categoría tiene muchos
productos (relación 1:N).

## Estructura

```
productos_api/
├── app/
│   ├── main.py              # crea la app, registra routers y el manejador de errores
│   ├── core/
│   │   ├── database.py      # conexión a PostgreSQL (lee DATABASE_URL de .env)
│   │   ├── dependencies.py  # get_db / SessionDep
│   │   └── exceptions.py    # NoEncontrado (404), Conflicto (409)
│   ├── models/              # Modelo: tablas SQLAlchemy
│   │   ├── categoria.py
│   │   └── producto.py
│   ├── schemas/             # validación de entrada y forma de las respuestas
│   │   ├── categoria.py
│   │   └── producto.py
│   ├── controllers/         # Controlador: consultas y reglas, sin nada de HTTP
│   │   ├── categorias.py
│   │   └── productos.py
│   └── routes/              # Vista/rutas: endpoints que llaman al controlador
│       ├── categorias.py
│       └── productos.py
├── docker-compose.yml       # PostgreSQL local (opcional)
├── .env.example
└── requirements.txt
```

**Cómo viaja una petición:**
`routes` (recibe y valida con `schemas`) → `controllers` (lógica y consultas con `models`) →
`routes` devuelve la respuesta con el `response_model`.

## Puesta en marcha

1. **PostgreSQL.** Con Docker: `docker compose up -d`. Si usas tu propio servidor, crea una
   base vacía: `CREATE DATABASE tienda;`
2. **Configuración.** Copia `.env.example` como `.env` y ajusta `DATABASE_URL`:

   ```
   DATABASE_URL=postgresql+psycopg://usuario:contrasena@host:5432/tienda
   ```

3. **Arrancar** (desde `clase-fast-api`):

   ```powershell
   .venv\Scripts\Activate.ps1
   pip install -r productos_api\requirements.txt
   cd productos_api
   uvicorn app.main:app --reload
   ```

Documentación interactiva: http://127.0.0.1:8000/docs. Las tablas se crean solas al arrancar.

## Endpoints

| Método   | Ruta                             | Descripción                                    | Respuestas      |
|----------|----------------------------------|------------------------------------------------|-----------------|
| `GET`    | `/categorias`                    | Lista categorías                               | 200             |
| `GET`    | `/categorias/{id}`               | Una categoría                                  | 200 / 404       |
| `GET`    | `/categorias/{id}/productos`     | Productos de una categoría                     | 200 / 404       |
| `POST`   | `/categorias`                    | Crea                                           | 201 / 409 / 422 |
| `PATCH`  | `/categorias/{id}`               | Actualiza los campos enviados                  | 200 / 404 / 409 |
| `DELETE` | `/categorias/{id}`               | Elimina (409 si tiene productos)               | 204 / 404 / 409 |
| `GET`    | `/productos`                     | Lista. Filtros: `categoria_id`, `buscar`, `solo_activos`, `skip`, `limit` | 200 |
| `GET`    | `/productos/{id}`                | Un producto con su categoría                   | 200 / 404       |
| `POST`   | `/productos`                     | Crea (404 si la categoría no existe)           | 201 / 404 / 409 / 422 |
| `PATCH`  | `/productos/{id}`                | Actualiza los campos enviados                  | 200 / 404 / 409 |
| `DELETE` | `/productos/{id}`                | Elimina                                        | 204 / 404       |

## Ejemplos para `/docs`

```json
POST /categorias
{ "nombre": "electrónica", "descripcion": "Equipos y accesorios" }

POST /productos
{ "nombre": "teclado mecánico", "precio": 149.99, "stock": 10, "categoria_id": 1 }

PATCH /productos/1
{ "precio": 129.99 }
```

Respuesta de un producto (la categoría va anidada):

```json
{
  "id": 1,
  "nombre": "Teclado mecánico",
  "descripcion": null,
  "precio": 149.99,
  "stock": 10,
  "activo": true,
  "creado_en": "2026-10-20T13:04:11.604221Z",
  "categoria": { "id": 1, "nombre": "Electrónica" }
}
```

## Reglas

- Los nombres de categoría y de producto son **únicos sin distinguir mayúsculas** (409).
- No se puede borrar una categoría con productos (409; además la FK es `RESTRICT`).
- `precio > 0`, `stock >= 0`. En `PATCH`, los campos enviados como `null` se ignoran.
