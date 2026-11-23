import os
from flask import Flask
from .extensions import db, migrate
from .config import config_by_name
from dotenv import load_dotenv
from .auth_routes import auth_bp
from .user_routes import user_bp
    
load_dotenv()  # Load environment variables from .env file




def create_app(config_name):
    config = config_by_name.get(config_name)
    if not config:
        raise ValueError("Invalid config name")
    app = Flask(__name__)
    app.config.from_object(config)
    print("CONFIG:", config_name, app.config.get("SQLALCHEMY_DATABASE_URI"))
    db.init_app(app)
    migrate.init_app(app, db)

    from .models import User
    from .routes import orders_bp

    @app.errorhandler(404)
    def not_found(error):
        return {
            "code": "NOT_FOUND",
            "message": "Resource not found"
        }, 404

    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/users")
    return app