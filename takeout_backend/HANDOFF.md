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

## Auth blueprints / Routes
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

## Password hashing & verification audit
- Dev DB: `instance/temp.db`
- Sample user: `test@example.com`
- `password_hash` starts with `scrypt:32768:8:1$...` (Werkzeug hash)
- Verification (via `flask shell`):
  - `check_password_hash(u.password_hash, "Secret123!")` → `True`
  - `check_password_hash(u.password_hash, "wrong-value")` → `False`
- Only one user in DB, created through the hashed registration flow; no plaintext passwords ever stored.

## Migrations
- Flask-Migrate initialized at project root.
- Latest migration: `8662ad333278_add_users_table.py` (creates `users` table as above).

## Next step
- Commit current work on the auth feature branch:
  - `git status` → confirm only intended files changed (e.g. `HANDOFF.md`)
  - `git add HANDOFF.md`
  - `git commit -m "chore(auth): document password hashing audit"`
  - `git push`
- Upcoming lessons:
  - Implement login endpoint using `check_password_hash` for credential verification
  - Add JWT issuance and protected routes later on