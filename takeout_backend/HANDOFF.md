# HANDOFF
- Try to keep around 100 lines; use more only if context is needed. Always put in the copy box to retain formatting.

## Project
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
  - `extensions.py` – db, migrate, etc.
  - `models.py` – `User` (with roles)
  - `routes.py` – `orders_bp` + protected health and admin-health checks
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
  - Active dev DB: `instance/example.db` (confirmed via `flask db upgrade` + sqlite3)
- JWT:
  - `JWT_SECRET` in env → `app.config["JWT_SECRET_KEY"]`
  - `JWT_LIFETIME_SECONDS` in env (default `3600`)

## Models
- `User` (`models.py`)
  - `__tablename__ = "users"`
  - `id` (int, PK)
  - `email` (String(120), unique, not null)
  - `password_hash` (String(128), not null)
  - `created_at` (DateTime, default `db.func.current_timestamp()`)
  - `role` (String(20), not null, default `"user"`; DB migration: `role VARCHAR(20) DEFAULT 'user' NOT NULL`)

## Auth blueprints / routes
- `auth_bp` (`auth_routes.py`)
  - `POST /auth/register`
    - Body: `email`, `password`
    - 400: `code: "VALIDATION_ERROR"`
    - 409: `code: "EMAIL_TAKEN"`
    - 201: `id`, `email`, `created_at`
  - `POST /auth/login`
    - Body: `email`, `password`
    - 400: `VALIDATION_ERROR`
    - 401: `INVALID_CREDENTIALS`
    - 200: `id`, `email`, `created_at`, `token`
      - JWT payload: `{"sub": "<user.id as string>", "role": user.role, "exp": <unix ts>}`

## Orders blueprint / routes
- `orders_bp` (`routes.py`)
  - Prefix: `/orders`
  - `GET /orders/health`
    - Protected by `@require_auth`
    - 200: `{"status": "healthy"}`
  - `GET /orders/admin/health`
    - `@require_auth` (JWT verification + sets `g.current_user_id`, `g.current_user_role`)
    - In-view role check: requires `g.current_user_role == "admin"`
    - 200 (admin): `{"status": "admin healthy"}`
    - 403 (non-admin): `{"error": "Unauthorized"}`
    - 401 (no/invalid token): from `@require_auth` (`{"code":"UNAUTHORIZED", ...}`)

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
  - `@require_auth` decorator:
    - Reads `Authorization: Bearer <token>`
    - Missing/invalid header → 401:
      - `{"code":"UNAUTHORIZED","message":"Missing or invalid Authorization header."}`
    - Decodes JWT with `JWT_SECRET_KEY`, HS256, requires `exp`
    - Sets `g.current_user_id = int(sub)` and `g.current_user_role` from the token’s `role` claim
    - Invalid/expired token → 401:
      - `{"code":"UNAUTHORIZED","message":"Invalid or expired token."}`

## Verified curl behavior (dev, port 5001)
- `GET /users/me` and `PATCH /users/me`:
  - Work only with a valid token
  - Always operate on the caller’s own `User`
- `GET /orders/admin/health`:
  - Admin token (`role: "admin"`) → 200, `{"status":"admin healthy"}`
  - Regular user token (`role: "user"`) → 403, `{"error":"Unauthorized"}`
  - No token → 401, `{"code":"UNAUTHORIZED","message":"Missing or invalid Authorization header."}`

## Up next
- Continue core resource design and CRUD with auth + roles enforced where needed.