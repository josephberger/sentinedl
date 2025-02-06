from flask import Flask
from app.config import Config  # Import config file
from app.database import init_db
from app.routes import edl_bp
from app.auth import auth_bp, login_manager, jwt
from app.api import api_bp
from app.user import user_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configuration

    # Initialize database
    init_db()

    # Initialize Flask Extensions
    jwt.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    app.register_blueprint(edl_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/users")  # Register user management

    return app
