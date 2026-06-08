from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    CORS(app)

    from app.routes.habits import habits_bp
    from app.routes.ai import ai_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(habits_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(auth_bp)

    return app