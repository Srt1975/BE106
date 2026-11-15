import jwt
from functools import wraps
from flask import request, jsonify, g, current_app
from .models import User

def require_auth(f):
    """
    Decorator to require authentication for a route.
    Checks for a valid JWT token in the Authorization header.
    If valid, sets g.user to the authenticated user.
    If invalid or missing, returns a 401 Unauthorized response.
    """
  
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"code": "UNAUTHORIZED", "message": "Missing or invalid Authorization header."}), 401
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"], options={"require": ["exp"], "verify_exp": True},)
            sub = payload.get("sub")
            if not sub:
                return jsonify({"code": "UNAUTHORIZED", "message": "Invalid token payload."}), 401
            g.current_user_id = int(sub)
        except (jwt.ExpiredSignatureError):
            return jsonify({"code": "UNAUTHORIZED", "message": "Expired token."}), 401
        except (jwt.InvalidTokenError):
            return jsonify({"code": "UNAUTHORIZED", "message": "Invalid token."}), 401
        
        return f(*args, **kwargs)
    return decorated_function