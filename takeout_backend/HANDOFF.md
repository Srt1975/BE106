# HANDOFF

## Project
- Name: takeout_backend
- Path: /Volumes/dev_n_game/school/BE105FINAL/takeout_backend

## Environment
- Python: 3.14.10
- Venv: ./venv
- Activate (macOS):
  - source venv/bin/activate

## Dependencies (core)
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- python-dotenv
- PyJWT
- Pinned in: requirements.txt

## Current structure
- Project root: BE105FINAL/takeout_backend/
  - `requirements.txt`
  - `wsgi.py` (calls `create_app("production")` or another config name as needed)
  - `.env` (untracked, real values)
  - `.env.example` (template / placeholders)
  - `.gitignore` (includes `.env`)
  - `HANDOFF.md` (this file)
- Package: BE105FINAL/takeout_backend/takeout_backend/
  - `__init__.py`
    - Defines `create_app(config_name)`
    - Calls `load_dotenv()` at import time
    - Looks up config class via `config_by_name[config_name]`
    - Applies it with `app.config.from_object(config)`
    - Prints `CONFIG: <name> <SQLALCHEMY_DATABASE_URI>` at startup (for now)
    - Registers `orders_bp` with prefix `/orders`
  - `config.py`
    - `class BaseConfig:`
      - `DEBUG = False`
      - `PORT = 5001`
      - `DATABASE_URL = os.environ.get("DATABASE_URL")`
      - `SQLALCHEMY_DATABASE_URI = DATABASE_URL if DATABASE_URL else "sqlite:///temp.db"`
      - `JWT_SECRET_KEY = os.environ.get("JWT_SECRET", "default")`
    - `class DevelopmentConfig(BaseConfig):`
      - `DEBUG = True`
    - `class TestingConfig(BaseConfig):`
      - `DEBUG = True`
      - `TESTING = True`
    - `class ProductionConfig(BaseConfig):`
      - `DEBUG = False`
      - `PORT = int(os.environ.get("PORT", 5001))`
    - `config_by_name = { "development": DevelopmentConfig, "testing": TestingConfig, "production": ProductionConfig }`
  - `extensions.py`
    - `db` (SQLAlchemy instance, with `init_app`)
    - `migrate` (Flask-Migrate instance, with `init_app`)
  - `routes.py`
    - `orders_bp` blueprint
    - Health endpoint:
      - Endpoint: `orders.health_check`
      - Method: `GET`
      - URL rule: `/orders/health`

## Config & environment behavior
- Configuration is selected at runtime via `create_app(config_name)`:
  - `"development"` → `DevelopmentConfig`
  - `"testing"` → `TestingConfig`
  - `"production"` → `ProductionConfig`
- `.env` is loaded via `python-dotenv` inside `__init__.py`.
- Database configuration:
  - `DATABASE_URL` read from environment / `.env`
  - `SQLALCHEMY_DATABASE_URI` set to:
    - `DATABASE_URL` if present
    - otherwise `sqlite:///temp.db` (dev-style fallback)
- JWT configuration:
  - `JWT_SECRET` read from environment / `.env`
  - Exposed to app as `app.config["JWT_SECRET_KEY"]`
- Verified behavior:
  - Changing `DATABASE_URL` in `.env` and restarting changes the printed `SQLALCHEMY_DATABASE_URI`.
  - `flask routes` shows:
    - `orders.health_check  GET  /orders/health`

## Next up
- Flesh out the `orders` domain:
  - Decide basic data model (what an order looks like).
  - Prepare to add SQLAlchemy models and migrations.
- Keep using non-5000 ports for local runs:
  - Example: `FLASK_APP=wsgi.py flask run --port 5001`
- Later milestones (not done yet, just planned):
  - Define models and run initial migrations
  - Add JWT-based auth using `JWT_SECRET_KEY`
  - Add more endpoints under `/orders` and future domains (`restaurants`, `users`, etc.)

## Notes / conventions
- Port 5000 is off-limits; use 5001+ for local dev.
- `.env` is **untracked** and must never be committed.
- `.env.example` documents required env vars:
  - `DATABASE_URL`
  - `JWT_SECRET`
- Swapping DBs later (e.g., to Postgres) should be done by updating `DATABASE_URL` in `.env` and restarting, without changing Python code.