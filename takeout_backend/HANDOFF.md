# HANDOFF
- Try to keep around 100 lines; use more only if context is needed.

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
  - `models.py` – `User`
  - `routes.py` – `orders_bp` + protected health check
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
  - `DATABASE_URL` from env if set, else `sqlite:///temp.db`
  - Active dev DB: `instance/temp.db` (confirmed via `db.engine.url`)
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
      - JWT payload: `{"sub": "<user.id as string>", "role": "user", "exp": <unix ts>}`

## Orders blueprint / routes
- `orders_bp` (`routes.py`)
  - Prefix: `/orders`
  - `GET /orders/health`
    - Protected by `@require_auth`
    - 200: `{"status": "healthy"}`

## User profile routes
- `user_bp` (`user_routes.py`)
  - Prefix: `/users`
  - `GET /users/me`
    - `@require_auth`, uses `g.current_user_id`
    - Returns `{id, email, created_at}` for the caller only
  - `PATCH /users/me`
    - `@require_auth`, uses `g.current_user_id`
    - Allowlist: updates `email` only
    - Ignores `password_hash` or other unexpected fields

## Auth utilities
- `auth_utils.py`
  - `@require_auth` decorator:
    - Reads `Authorization: Bearer <token>`
    - Missing/invalid → 401:
      - `{"code":"UNAUTHORIZED","message":"Missing or invalid Authorization header."}`
    - Decodes JWT with `JWT_SECRET_KEY`, HS256, requires `exp`
    - Sets `g.current_user_id = int(sub)`
    - Invalid/expired → 401:
      - `{"code":"UNAUTHORIZED","message":"Invalid or expired token."}`

## Verified curl behavior (dev, port 5001)
- Both `GET /users/me` and `PATCH /users/me`:
  - Work only with a valid token
  - Always operate on the caller’s own `User` (tested with two accounts)