# README

## Setup

Assuming you have the GitHub CLI installed:

- `gh repo clone Srt1975/BE106`
- `cd BE106/takeout_backend`
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `cp .env.example .env`  # then edit .env and add real values
- `export FLASK_APP=wsgi.py`
- `export FLASK_RUN_PORT=5001`
- `flask run`

## Environment variables

This project uses a `.env` file for configuration. Start by copying the example file:

- `cp .env.example .env`

Then edit `.env` and set real values:

- `DATABASE_URL`: SQLAlchemy database URL (e.g. `sqlite:///temp.db` or a Postgres URL).  
  If not set, the app falls back to `sqlite:///temp.db` (stored at `instance/temp.db`).
- `JWT_SECRET`: secret key used to sign JWTs. Use a long, random string in real environments.
- `JWT_LIFETIME_SECONDS`: lifetime of access tokens in seconds (default `3600` if not set).

The `.env.example` file contains placeholders only and should never include real secrets.

## Migrations

This project uses Flask-Migrate for database migrations.

After setting up the project and `.env`:

- `flask db init`        # only the first time, to create the migrations folder  
- `flask db migrate -m "Initial migration"`  
- `flask db upgrade`

## Authentication

### Register

`POST /auth/register`

Body (JSON):

```json
{
  "email": "test@example.com",
  "password": "plaintext-password"
}