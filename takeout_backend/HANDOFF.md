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
  - `auth_utils.py` – JWT auth decorator

## App config
- `create_app(config_name)` uses `config_by_name` and registers:
  - `auth_bp` at `/auth`
  - `orders_bp` at `/orders`
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
    - Body: `email`, `password` (strings)
    - 400 on missing/empty fields:
      - `code: "VALIDATION_ERROR"`
    - 409 on duplicate email:
      - `code: "EMAIL_TAKEN"`
    - 201 on success:
      - `id`, `email`, `created_at` (no password/hash in response)
  - `POST /auth/login`
    - Body: `email`, `password`
    - 400 on missing/empty fields (`VALIDATION_ERROR`)
    - Looks up `User` by `email`, checks `check_password_hash(...)`
    - 401 on bad credentials:
      - `code: "INVALID_CREDENTIALS"`
    - 200 on success:
      - Returns user info + JWT:
        ```json
        {
          "id": <int>,
          "email": "<string>",
          "created_at": "<ISO timestamp or null>",
          "token": "<JWT string>"
        }
        ```
      - JWT payload:
        ```json
        {
          "sub": "<user.id as string>",
          "role": "user",
          "exp": <unix timestamp, now + JWT_LIFETIME_SECONDS>
        }
        ```
      - Encoded with PyJWT `jwt.encode(...)`:
        - Secret: `current_app.config["JWT_SECRET_KEY"]`
        - Algorithm: `HS256`

## Orders blueprint / routes
- `orders_bp` (`routes.py`)
  - Prefix: `/orders`
  - `GET /orders/health`
    - Protected by `@require_auth`
    - 200 on valid token:
      ```json
      {"status": "healthy"}
      ```

## Auth utilities
- `auth_utils.py`
  - `@require_auth` decorator:
    - Reads `Authorization` header, expects `Bearer <token>`.
    - On missing/invalid header:
      - 401 with:
        ```json
        {
          "code": "UNAUTHORIZED",
          "message": "Missing or invalid Authorization header."
        }
        ```
    - Decodes JWT with `current_app.config["JWT_SECRET_KEY"]`, `HS256`.
    - Extracts `sub`, converts to `int`, sets `g.current_user_id`.
    - On invalid/expired token or bad payload:
      - 401 with:
        ```json
        {
          "code": "UNAUTHORIZED",
          "message": "Invalid or expired token."
        }
        ```

## Password hashing audit
- Dev DB: `instance/temp.db`
- Sample user: `test@example.com`
- `password_hash` starts with `scrypt:32768:8:1$...` (Werkzeug)
- Verified via `flask shell` using `check_password_hash`.

## Verified curl behavior (dev, port 5001)
- No token:
  ```bash
  curl -i http://localhost:5001/orders/health
  ```
  → `401 UNAUTHORIZED`, body:
  `{"code":"UNAUTHORIZED","message":"Missing or invalid Authorization header."}`

- Tampered token:
  ```bash
  curl -i -H "Authorization: Bearer <TAMPERED_TOKEN>" \
    http://localhost:5001/orders/health
  ```
  → `401 UNAUTHORIZED`, body:
  `{"code":"UNAUTHORIZED","message":"Invalid or expired token."}`

- Valid token:
  ```bash
  curl -i -H "Authorization: Bearer <REAL_TOKEN>" \
    http://localhost:5001/orders/health
  ```
  → `200 OK`, body:
  `{"status":"healthy"}`