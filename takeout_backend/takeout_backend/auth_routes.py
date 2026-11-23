from flask import Blueprint, request, jsonify, current_app
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .extensions import db


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    field_errors = {}
    if not email:
        field_errors["email"] = "Email is required."
    if not password:
        field_errors["password"] = "Password is required."
    if field_errors:
        error_body = {
            "code": "VALIDATION_ERROR",
            "message": "There were validation errors.",
            "fields": field_errors,
        }
        return jsonify(error_body), 400
    existing = User.query.filter_by(email=email).first()
    if existing:
        error_body = {
            "code": "EMAIL_TAKEN",
            "message": "Email is already registered."
        }
        return jsonify(error_body), 409
    hashed = generate_password_hash(password)
    user = User(email=email, password_hash=hashed)
    db.session.add(user)
    db.session.commit()

    response_body = {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }
    return jsonify(response_body), 201
    
@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    field_errors = {}
    if not email:
        field_errors["email"] = "Email is required."
    if not password:
        field_errors["password"] = "Password is required."
    if field_errors:
        error_body = {
            "code": "VALIDATION_ERROR",
            "message": "There were validation errors.",
            "fields": field_errors,
        }
        return jsonify(error_body), 400
   
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        error_body = {
            "code": "INVALID_CREDENTIALS",
            "message": "Invalid email or password."
        }
        return jsonify(error_body), 401

    # Get UTC time for token creation
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    exp = now + timedelta(seconds=current_app.config["JWT_LIFETIME_SECONDS"])

    payload = {
    "sub": str(user.id),
    "role": user.role,
    "exp": int(exp.timestamp()),
}
    token = jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")

    response_body = {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "token": token
    }
    return jsonify(response_body), 200   
   