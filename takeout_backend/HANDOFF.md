# Takeout Backend – HANDOFF

Python 3.14.10 • Flask API for delivery orders with JWT auth.  
Repo: BE106/takeout_backend • Dev: http://localhost:5001

## Setup

python3 -m venv venv  
source venv/bin/activate  
pip install -r requirements.txt  

flask db upgrade          # migrations  
flask --app wsgi:app run --port 5001

Env via .env (from .env.example):

- FLASK_ENV=development
- DATABASE_URL (default sqlite:///example.db)
- JWT_SECRET (required)
- JWT_LIFETIME_SECONDS (default 3600)

DB file: instance/example.db

## Structure

- wsgi.py – entrypoint, calls create_app
- takeout_backend/__init__.py – app factory, blueprints, 404 handler
- takeout_backend/config.py – config_by_name
- takeout_backend/extensions.py – db, migrate
- takeout_backend/models.py – User, DeliveryOrder
- takeout_backend/routes.py – orders_bp (orders + health)
- takeout_backend/auth_routes.py – auth_bp (register/login)
- takeout_backend/user_routes.py – user_bp (current user)
- takeout_backend/auth_utils.py – @require_auth

create_app(config_name):

- loads env, applies config_by_name[config_name]
- initializes db and migrate
- imports models so migrations see them
- registers blueprints:
  - auth_bp → /auth
  - orders_bp → /orders
  - user_bp → /users
- registers JSON 404 handler:
  - 404 → {"code":"NOT_FOUND","message":"Resource not found"}

## Data Model

User:

- id, email (unique), password_hash, role ("user" default), created_at
- relationship: delivery_orders (one-to-many)

DeliveryOrder:

- id (PK)
- user_id (FK → users.id, NOT NULL, owner field)
- restaurant_name (required)
- total_price (float, required)
- special_instructions (nullable)
- reference_number (unique, required)

Ownership:

- user_id always set from g.current_user_id on create
- never read from request body

## Auth

Header: Authorization: Bearer <token>

JWT payload:

- sub: user.id as string
- role: user.role
- exp: unix timestamp

@require_auth:

- on success: sets g.current_user_id, g.current_user_role
- on failure: 401 with code UNAUTHORIZED (missing/invalid header, invalid token)

## Routes

### /auth

POST /auth/register

- body: email, password
- 400 VALIDATION_ERROR ({"code","message","fields"})
- 409 EMAIL_TAKEN
- 201 {id,email,created_at}

POST /auth/login

- body: email, password
- 400 VALIDATION_ERROR
- 401 INVALID_CREDENTIALS
- 200 {id,email,created_at,token}

### /users

GET /users/me

- auth required, uses g.current_user_id
- 200 {id,email,created_at}

PATCH /users/me

- auth required
- updates email only
- 200 updated user JSON

### /orders – health

GET /orders/health

- auth required
- 200 {"status":"healthy"}

GET /orders/admin/health

- auth required, role must be "admin"
- admin: 200 {"status":"admin healthy"}
- non-admin: 403 {"code":"FORBIDDEN","message":"You do not have permission to access this resource."}

## Delivery Orders

Base path: /orders/orders (auth required for all)

POST /orders/orders

- body: restaurant_name, total_price, reference_number
- sets user_id = g.current_user_id
- 400 VALIDATION_ERROR for bad/missing fields:
  - {"code":"VALIDATION_ERROR","message":"There were validation errors.","fields":{...}}
- 201 {"message":"Delivery order created successfully","data":{id,user_id,...}}

GET /orders/orders

- returns only orders where user_id == g.current_user_id
- 200 {"data":[{id,restaurant_name,total_price,reference_number},...]}

## Ownership Enforcement

GET /orders/orders/<order_id>

- fetch by PK
- if not found: 404 {"code":"NOT_FOUND","message":"Delivery order not found"}
- if order.user_id != g.current_user_id: same 404
- owner: 200 {"data":{id,restaurant_name,total_price,reference_number}}

PATCH /orders/orders/<order_id>

- fetch by PK; if not found: 404 NOT_FOUND
- parse JSON (silent=True); if None: 400 INVALID_JSON
- if order.user_id != g.current_user_id: 404 NOT_FOUND
- update restaurant_name / total_price / reference_number
- commit; 200 {"message":"Delivery order updated successfully","data":{...}}

DELETE /orders/orders/<order_id>

- fetch by PK; if not found: 404 NOT_FOUND
- if order.user_id != g.current_user_id: 404 NOT_FOUND
- delete + commit; 200 {"message":"Delivery order deleted successfully"}