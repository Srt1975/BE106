# HANDOFF
- try to keep around 100 lines use more only if context is needed.

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
  - `JWT_LIFETIME_SECONDS` in env (default `3600`) → `app.config["JWT_LIFETIME_SECONDS"]`

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
    - Duplicate email:
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
  - `POST /auth/login`
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
    - Credential check:
      - Looks up `User` by `email`
      - Uses `check_password_hash(user.password_hash, password)` for verification
    - Failure (unknown email or wrong password):
      - Always returns the same `401`:
        ```json
        {
          "code": "INVALID_CREDENTIALS",
          "message": "Invalid email or password."
        }
        ```
    - Success:
      - Builds JWT payload:
        ```json
        {
          "sub": "<user.id as string>",
          "role": "user",
          "exp": <unix timestamp, UTC now + JWT_LIFETIME_SECONDS>
        }
        ```
      - Uses:
        - Secret: `current_app.config["JWT_SECRET_KEY"]`
        - Lifetime: `current_app.config["JWT_LIFETIME_SECONDS"]`
        - Algorithm: `HS256`
      - Encodes with PyJWT’s `jwt.encode(...)`
      - Returns `200` with:
        ```json
        {
          "id": <int>,
          "email": "<string>",
          "created_at": "<ISO timestamp or null>",
          "token": "<JWT string>"
        }
        ```

## Password hashing & verification audit
- Dev DB: `instance/temp.db`
- Sample user: `test@example.com`
- `password_hash` starts with `scrypt:32768:8:1$...` (Werkzeug hash)
- Verification (via `flask shell`):
  - `check_password_hash(u.password_hash, "Secret123!")` → `True`
  - `check_password_hash(u.password_hash, "wrong-value")` → `False`
- Only one user in DB, created through the hashed registration flow; no plaintext passwords ever stored.

## JWT issuance audit
- Successful login (`test@example.com` / `Secret123!`) via `curl`:
  - Returns `200 OK` with `token` in JSON body.
- Local decode with `jwt.decode(token, options={"verify_signature": False})` shows:
  - `sub` is a string `"1"`
  - `role` is `"user"`
  - `exp` is a numeric Unix timestamp in the future.
- Wrong email and wrong password both return identical `401 INVALID_CREDENTIALS` responses.

## Migrations
- Flask-Migrate initialized at project root.
- Latest migration: `8662ad333278_add_users_table.py` (creates `users` table as above).

## Next step
- Verify branch is clean and push:
  - `git status`
  - `git add takeout_backend/auth_routes.py takeout_backend/config.py HANDOFF.md`
  - `git commit -m "feat(auth): implement login with JWT issuance"`
  - `git push`
- Upcoming lessons:
  - Use this JWT to protect routes
  - Enforce access based on the token’s identity/role