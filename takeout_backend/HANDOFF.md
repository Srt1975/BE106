# HANDOFF

## Project
- Repo root: BE106 
- Name: takeout_backend
- Path: /Volumes/dev_n_game/school/BE106/takeout_backend

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
- Repo root:
  -  `.gitignore` (includes `.env`)
- Project root: BE106/takeout_backend/
  - `requirements.txt`
  - `wsgi.py` (calls `create_app("production")` or another config name as needed)
  - `.env` (untracked, real values)
  - `.env.example` (template / placeholders)
  - `HANDOFF.md` (this file)
  - `README.md` now documents setup, env vars and migrations info
- Package: BE106/takeout_backend/takeout_backend/
  - `__init__.py`
    - Defines `create_app(config_name)`
    - Calls `load_dotenv()` at import time
    - Looks up config class via `config_by_name[config_name]`
    - Applies it with `app.config.from_object(config)`
    - Initializes db and migrate from extensions
    - Imports User from .models so Flask-Migrate can see it
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
  - models.py
    - class User(db.Model):
    - __tablename__ = "users"
    - id: integer primary key
    - email: String(120), unique, nullable=False
    - password_hash: String(128), nullable=False
    - created_at: DateTime, default db.func.current_timestamp()
    - __repr__ returns <User {email}>
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
    - flask db migrate and flask db upgrade operate on the DB indicated by SQLALCHEMY_DATABASE_URI.

## Database & migrations
  - Migrations initialized with flask db init at project root.
  - Current active dev DB:
    - URL: sqlite:///temp.db
    - File path: instance/temp.db (confirmed via db.engine.url)
  - Latest migration:
    - File: migrations/versions/8662ad333278_add_users_table.py
    - Message: "Add users table"
    - upgrade() creates users table with:
      - id (PK, integer, not null)
      - email (String(120), not null, unique)
      - password_hash (String(128), not null)
      - created_at (DateTime)
  - SQLite schema (from .schema users in instance/temp.db):
      CREATE TABLE users (
        id INTEGER NOT NULL,
        email VARCHAR(120) NOT NULL,
        password_hash VARCHAR(128) NOT NULL,
        created_at DATETIME,
        PRIMARY KEY (id),
        UNIQUE (email)
    );


## Notes / conventions
- Port 5000 is off-limits; use 5001+ for local dev.
- `.env` is **untracked** and must never be committed.
- `.env.example` documents required env vars:
  - `DATABASE_URL`
  - `JWT_SECRET`
- Swapping DBs (e.g., to Postgres) should be done by updating           DATABASE_URL in .env and restarting, plus flask db upgrade against the new DB, without changing Python code.
- For migrations to see models:
    -User and future models must be imported in create_app (or otherwise imported on app startup).