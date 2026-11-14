# HANDOFF

## Project
- Repo: `BE106/takeout_backend`
- Python: 3.14.10
- Venv: `./venv` → `source venv/bin/activate`

## Dependencies
- Flask, Flask-SQLAlchemy, Flask-Migrate
- python-dotenv, PyJWT
- Pinned in `requirements.txt`

## Structure
- Root: `.gitignore`, `requirements.txt`, `wsgi.py`, `.env`, `.env.example`, `HANDOFF.md`, `README.md`
- Package: `takeout_backend/`
  - `__init__.py`
  - `config.py`
  - `extensions.py`
  - `models.py`
  - `routes.py` (orders)
  - `auth_routes.py` (auth)

## App config
- `create_app(config_name)` with `config_by_name`
- `.env` loaded via `load_dotenv()` in `__init__.py`
- DB:
  - `DATABASE_URL` from env if set
  - Else fallback: `sqlite:///temp.db`
  - Active dev DB: `instance/temp.db` (confirmed via `db.engine.url`)
- JWT:
  - `JWT_SECRET` in env → `app.config["JWT_SECRET_KEY"]`

## Models
- `User` (`models.py`)
  - `__tablename__ = "users"`
  - `id` (int, PK)
  - `email` (String(120), unique, not null)
  - `password_hash` (String(128), not null)
  - `created_at` (DateTime, default `db.func.current_timestamp()`)

## Blueprints / Routes
- `orders_bp` (`routes.py`)
  - Prefix: `/orders`
  - `GET /orders/health` → health check
- `auth_bp` (`auth_routes.py`)
  - Prefix: `/auth`
  - `POST /auth/register`
    - Request JSON:
      - `email` (string)
      - `password` (string)
    - Validation:
      - Missing/empty fields → `400` with:
        ```json
        {
          "code": "VALIDATION_ERROR",
          "message": "There were validation errors.",
          "fields": {
            "email": "...optional...",
            "password": "...optional..."
          }
        }
        ```
    - Duplicate email (`users.email` unique):
      - `409` with:
        ```json
        {
          "code": "EMAIL_TAKEN",
          "message": "Email is already registered."
        }
        ```
    - Success:
      - Hashes password with `generate_password_hash(password)`
      - Stores in `User.password_hash`
      - Returns `201` with:
        ```json
        {
          "id": <int>,
          "email": "<string>",
          "created_at": "<ISO timestamp or null>"
        }
        ```
      - Never returns password or hash

## Migrations
- Flask-Migrate initialized at project root.
- Latest migration: `8662ad333278_add_users_table.py` (creates `users` table as above).

## Next step
- Commit current work on a feature branch:
  - `git status` → verify only auth + related files changed
  - Commit message suggestion:
    - `feat(auth): add registration endpoint with validation and duplicate handling`
- Upcoming lessons: login endpoint, JWT issuance, protected routes (not implemented yet).