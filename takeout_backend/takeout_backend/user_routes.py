from .models import User
from flask import Blueprint, jsonify, g, request
from .auth_utils import require_auth
from .extensions import db

user_bp = Blueprint("user", __name__)
@user_bp.get('/me')
@require_auth
def me():
    user = User.query.get(g.current_user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None
    })

@user_bp.route('/me', methods=['PATCH'])
@require_auth
def update_me():
    user = User.query.get(g.current_user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    email = data.get("email")

    if email:
        user.email = email

    db.session.commit()

    return jsonify({
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None
    })