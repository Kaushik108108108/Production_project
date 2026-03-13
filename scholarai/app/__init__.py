from flask import Flask
from .routes.auth import auth_bp
from .routes.admin import admin_bp
from .routes.student import student_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = 'scholarai-secret-key-change-in-production'

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp,   url_prefix='/admin')
    app.register_blueprint(student_bp, url_prefix='/student')

    return app
