# Takeout Backend – HANDOFF

Python 3.14.10 • Flask API for delivery orders with JWT auth.
Repo: BE106/takeout_backend • Dev: http://localhost:5001

---

## Setup

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

flask db upgrade          # apply migrations
flask --app wsgi:app run --port 5001

Env via .env (copy from .env.example):

- FLASK_ENV=development
- DATABASE_URL (optional, defaults to sqlite:///example.db)
- JWT_SECRET (required)
- JWT_LIFETIME_SECONDS (default 3600)

DB default: sqlite:///example.db → instance/example.db.

---

## Structure

- wsgi.py – entrypoint, calls create_app
- takeout_backend/__init__.py – app factory, env load, blueprints
- takeout_backend/config.py – config classes, config_by_name
- takeout_backend/extensions.py – db, migrate
- takeout_backend/models.py – User, DeliveryOrder
- takeout_backend/routes.py – orders_bp (orders + health)
- takeout_backend/auth_routes.py – auth_bp (register/login)
- takeout_backend/user_routes.py – user_bp (/users/me)
- takeout_backend/auth_utils.py – @require_auth JWT decorator

create_app(config_name):

- loads env with load_dotenv()
- uses config_by_name[config_name]
- registers /auth, /orders, /users blueprints.

---

## Data Model

User

- id, email (unique), password_hash, role ("user" default), created_at
- relationship: delivery_orders – one-to-many to DeliveryOrder

DeliveryOrder

- id (PK)
- user_id (FK → users.id, not null; owner)
- restaurant_name (required)
- total_price (float, required)
- special_instructions (nullable)
- reference_number (unique, required)

user_id is always set from g.current_user_id on create; never trusted from request body.

---

## Auth

JWT in header:

Authorization: Bearer <token>

Token payload:

{ "sub": "<user.id as string>", "role": "<user.role>", "exp": <unix ts> }

@require_auth:

- on success: sets g.current_user_id, g.current_user_role
- on failure: 401 {"code":"UNAUTHORIZED","message":"Missing or invalid Authorization header."}

---

## Routes

Auth (/auth)

POST /auth/register
- Body: email, password
- 400 {"code":"VALIDATION_ERROR"}
- 409 {"code":"EMAIL_TAKEN"}
- 201 {id, email, created_at}

POST /auth/login
- Body: email, password
- 400 {"code":"VALIDATION_ERROR"}
- 401 {"code":"INVALID_CREDENTIALS"}
- 200 {id, email, created_at, token}

---

User (/users)

GET /users/me
- auth required; uses g.current_user_id
- returns {id, email, created_at}

PATCH /users/me
- auth required
- allowlist: email only

---

Orders (/orders)

Health:

GET /orders/health
- auth required
- 200 {"status":"healthy"}

GET /orders/admin/health
- auth required, g.current_user_role == "admin"
- admin: 200 {"status":"admin healthy"}
- non-admin: 403 {"error":"Unauthorized"}

Core orders (all auth required):

POST /orders/orders
- Body: restaurant_name, total_price, reference_number
- invalid JSON: 400 {"code":"INVALID_JSON"}
- missing fields: 400 {"code":"VALIDATION_ERROR"}
- sets user_id = g.current_user_id
- 201 {"message":"Delivery order created successfully","data":{id, user_id, restaurant_name, total_price, reference_number}}

GET /orders/orders
- returns only orders where user_id == g.current_user_id
- 200 {"data":[{id, restaurant_name, total_price, reference_number}, ...]}

GET /orders/orders/<int:order_id>
- looks up by PK, no ownership check yet
- 200 {"data":{...}} or
  404 {"code":"NOT_FOUND","message":"Delivery order not found"}

PATCH /orders/orders/<int:order_id>
- no ownership check yet
- data = request.get_json(silent=True)
  - None → 400 {"code":"INVALID_JSON","message":"Invalid JSON body"}
- updates any of: restaurant_name, total_price, reference_number
- not found → 404 {"code":"NOT_FOUND","message":"Delivery order not found"}
- success → 200 {"message":"Delivery order updated successfully","data":{...}}

DELETE /orders/orders/<int:order_id>
- no ownership check yet
- not found → 404 {"code":"NOT_FOUND","message":"Delivery order not found"}
- success → 200 {"message":"Delivery order deleted successfully"}

---

## Known Gap (Intentional for Now)

Any authenticated user can GET / PATCH / DELETE any DeliveryOrder by ID.
This is a missing authorization/ownership check, not an auth bug.
Next step (future lesson): enforce order.user_id == g.current_user_id for these endpoints.