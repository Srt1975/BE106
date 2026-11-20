## Project
- Max HANDOFF.md length @ about 100 lines
- Repo: `BE106/takeout_backend`
- Python: 3.14.10  
- Venv: `./venv` → `source venv/bin/activate`
- Default dev port: `5001`

## Dependencies
- Flask, Flask-SQLAlchemy, Flask-Migrate  
- python-dotenv, PyJWT, Werkzeug  
- Pinned in `requirements.txt`

## Structure
- Root: `.gitignore`, `requirements.txt`, `wsgi.py`, `.env`, `.env.example`, `HANDOFF.md`, `README.md`
- Package: `takeout_backend/`
  - `__init__.py` – app factory, env loading, blueprint registration
  - `config.py` – config classes, `config_by_name`
  - `extensions.py` – `db`, `migrate`, etc.
  - `models.py` – `User`, `DeliveryOrder` + relationships
  - `routes.py` – `orders_bp` (health, admin-health, delivery order create + list)
  - `auth_routes.py` – `auth_bp` (register + login)
  - `user_routes.py` – `user_bp` (`/users/me` GET + PATCH)
  - `auth_utils.py` – JWT auth decorator

## App config
- `create_app(config_name)` uses `config_by_name` and registers:
  - `auth_bp` at `/auth`
  - `orders_bp` at `/orders`
  - `user_bp` at `/users`
- `.env` loaded via `load_dotenv()` in `__init__.py`.
- DB:
  - `DATABASE_URL` from env if set, else `sqlite:///example.db`
  - Active dev DB: `instance/example.db` (via `flask db upgrade` + sqlite3)
- JWT:
  - `JWT_SECRET` in env → `app.config["JWT_SECRET_KEY"]`
  - `JWT_LIFETIME_SECONDS` in env (default `3600`)

## Models
- `User` (`models.py`)
  - `id`, `email` (unique), `password_hash`, `created_at`, `role` (default `"user"`)
  - `delivery_orders` – one-to-many to `DeliveryOrder`
- `DeliveryOrder` (`models.py`)
  - `id` (PK)
  - `user_id` (FK → `users.id`, not null) — owner of the order
  - `restaurant_name` (String(120), not null)
  - `total_price` (Float, not null)
  - `special_instructions` (Text, nullable)
  - `reference_number` (String(50), unique, not null)
  - `user` – many-to-one back to `User`
  - `user_id` is always set from `g.current_user_id` (JWT), never trusted from request body

## Auth routes
- `auth_bp` (`auth_routes.py`)
  - `POST /auth/register`
    - Body: `email`, `password`
    - 400: `{"code": "VALIDATION_ERROR"}`
    - 409: `{"code": "EMAIL_TAKEN"}`
    - 201: `id`, `email`, `created_at`
  - `POST /auth/login`
    - Body: `email`, `password`
    - 400: `{"code": "VALIDATION_ERROR"}`
    - 401: `{"code": "INVALID_CREDENTIALS"}`
    - 200: `id`, `email`, `created_at`, `token`
      - JWT payload: `{"sub": "<user.id as string>", "role": user.role, "exp": <unix ts>}`

## Orders routes
- `orders_bp` (`routes.py`)
  - Prefix: `/orders`
  - `GET /orders/health`
    - `@require_auth`
    - 200: `{"status": "healthy"}`
  - `GET /orders/admin/health`
    - `@require_auth` (sets `g.current_user_id`, `g.current_user_role`)
    - Requires `g.current_user_role == "admin"`
    - 200 (admin): `{"status": "admin healthy"}`
    - 403 (non-admin): `{"error": "Unauthorized"}`
    - 401 (no/invalid token): from `@require_auth` (`{"code":"UNAUTHORIZED", ...}`)
  - `POST /orders/orders`
    - `@require_auth`
    - JSON: `restaurant_name`, `total_price`, `reference_number` (required)
    - 400 invalid JSON: `{"code": "INVALID_JSON"}`
    - 400 missing fields: `{"code": "VALIDATION_ERROR"}`
    - Creates `DeliveryOrder` with `user_id = g.current_user_id`
    - 201: `{"message": "...", "data": {id, user_id, restaurant_name, total_price, reference_number}}`
  - `GET /orders/orders`
    - `@require_auth`
    - Returns only orders where `user_id == g.current_user_id`
    - 200: `{"data": [{id, restaurant_name, total_price, reference_number}, ...]}`

## User profile routes
- `user_bp` (`user_routes.py`)
  - Prefix: `/users`
  - `GET /users/me`
    - `@require_auth`, uses `g.current_user_id`
    - Returns `{id, email, created_at}` for the caller only
  - `PATCH /users/me`
    - `@require_auth`, uses `g.current_user_id`
    - Allowlist: updates `email` only
    - Ignores `password_hash`, `role`, or other unexpected fields

## Auth utilities
- `auth_utils.py`
  - `@require_auth`:
    - Reads `Authorization: Bearer <token>`
    - Verifies JWT
    - On success sets `g.current_user_id`, `g.current_user_role`
    - On failure returns 401 with `{"code": "UNAUTHORIZED", ...}`