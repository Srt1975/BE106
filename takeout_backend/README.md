# Takeout Backend

Flask API for delivery orders with JWT auth.

## Setup (local, SQLite)

Assuming you have the GitHub CLI installed:

- gh repo clone Srt1975/BE106
- cd BE106/takeout_backend
- python3 -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt
- cp .env.example .env    # then edit .env and add real values
- export FLASK_APP=wsgi.py
- export FLASK_RUN_PORT=5001
- flask run

## Environment variables

This project uses a `.env` file for configuration. Start by copying the example file:

- cp .env.example .env

Then edit `.env` and set real values:

- DATABASE_URL – SQLAlchemy database URL (e.g. sqlite:///temp.db or a Postgres URL).  
  If not set, the app falls back to sqlite:///temp.db (stored at instance/temp.db).
- JWT_SECRET – secret key used to sign JWTs. Use a long, random string in real environments.
- JWT_LIFETIME_SECONDS – lifetime of access tokens in seconds (default 3600 if not set).

`.env.example` contains placeholders only and should never include real secrets.

## Migrations (general)

After setting up the project and `.env`, you can use Flask-Migrate:

- flask db migrate -m "Describe change"
- flask db upgrade

## Authentication (local or Compose)

### Register

POST /auth/register

Body (JSON):

{
  "email": "test@example.com",
  "password": "plaintext-password"
}

### Login

POST /auth/login

Body (JSON):

{
  "email": "test@example.com",
  "password": "plaintext-password"
}

On success you receive a JWT token; send it as:

Authorization: Bearer <TOKEN>

## Running with Docker Compose (Postgres)

### Prerequisites

- Docker and Docker Compose installed
- .env file created from .env.example

At minimum, set:

- JWT_SECRET – any non-empty string
- You do not need to set DATABASE_URL when using Docker Compose; it is provided by docker-compose.yml.

### Start the stack and run migrations

From the project root:

- docker compose up -d --build
- docker exec -it takeout_backend-web-1 flask db upgrade    # first time only or after schema changes

The API is now available at http://localhost:5001 and uses Postgres in the db service.

### Smoke test (Compose)

1. Register:

   - POST /auth/register with a JSON body like:
     {
       "email": "compose_user@example.com",
       "password": "test1234"
     }

2. Login:

   - POST /auth/login with the same credentials and copy the token from the response.

3. Auth health check:

   - GET /orders/health with header:
     Authorization: Bearer <TOKEN_FROM_LOGIN>

4. Create a delivery order:

   - POST /orders/orders with header:
     Authorization: Bearer <TOKEN_FROM_LOGIN>
     and body:
     {
       "restaurant_name": "Compose Diner",
       "total_price": 19.99,
       "reference_number": "COMP-123"
     }

5. List orders:

   - GET /orders/orders with the same Authorization header; you should see the created order.

### Restart and persistence check

To verify that Postgres data is persisted via the db_data volume:

- docker compose down
- docker compose up -d --build

Then call:

- GET /orders/orders with a valid Authorization header.

The previously created order should still be present.