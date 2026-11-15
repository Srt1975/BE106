## Project summary (short)

- **Repo / env**
  - Repo: `BE106/takeout_backend`
  - Python: 3.14.10, venv: `./venv` → `source venv/bin/activate`
  - Dev port: `5001`
  - Dev DB: `instance/temp.db` (`DATABASE_URL=sqlite:///temp.db`)

- **Tech / structure**
  - Flask, Flask‑SQLAlchemy, Flask‑Migrate, python-dotenv, PyJWT, Werkzeug
  - Package: `takeout_backend/`
    - `__init__.py` – `load_dotenv()`, `create_app(config_name)`, register blueprints
    - `config.py` – `BaseConfig`, `config_by_name`, `JWT_LIFETIME_SECONDS` from env (default `3600`)
    - `extensions.py` – `db`, `migrate`
    - `models.py` – `User`
    - `auth_routes.py` – `auth_bp` (`/auth`)
    - `routes.py` – `orders_bp` (`/orders`)
    - `auth_utils.py` – `require_auth` decorator

- **Models**
  - `User`:
    - `id` (PK), `email` (unique, not null), `password_hash`, `created_at`
    - Passwords hashed with Werkzeug (`scrypt:...`)

- **Auth**
  - `POST /auth/register`
    - Validates `email` / `password`
    - 400: `VALIDATION_ERROR`, 409: `EMAIL_TAKEN`
    - 201: returns `id`, `email`, `created_at`
  - `POST /auth/login`
    - Validates `email` / `password`
    - 400: `VALIDATION_ERROR`, 401: `INVALID_CREDENTIALS`
    - 200: returns user + JWT:
      - Payload: `{"sub": "<user.id>", "role": "user", "exp": <unix timestamp>}`
      - `exp` = `datetime.now(timezone.utc) + JWT_LIFETIME_SECONDS`
      - Encoded with PyJWT HS256 + `JWT_SECRET_KEY`

- **JWT / protection**
  - `require_auth` (`auth_utils.py`):
    - Expects `Authorization: Bearer <token>`
    - Missing/invalid header → 401:
      - `{"code":"UNAUTHORIZED","message":"Missing or invalid Authorization header."}`
    - Decodes with:
      - `jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], options={"require": ["exp"], "verify_exp": True})`
    - On success: reads `sub`, sets `g.current_user_id = int(sub)`
    - Errors:
      - `ExpiredSignatureError` → 401:
        - `{"code":"UNAUTHORIZED","message":"Expired token."}`
      - `InvalidTokenError` → 401:
        - `{"code":"UNAUTHORIZED","message":"Invalid token."}`

- **Protected routes**
  - `GET /orders/health` (`orders_bp`):
    - Uses `@require_auth`
    - 200: `{"status":"healthy"}`

- **Next step**
  - Add core resource models + CRUD, protect routes with `require_auth` as needed.