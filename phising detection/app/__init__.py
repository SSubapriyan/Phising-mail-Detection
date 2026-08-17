from flask import Flask, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.ocr import bp as ocr_bp
    app.register_blueprint(ocr_bp, url_prefix='/ocr')

    from app.ml import bp as ml_bp
    app.register_blueprint(ml_bp, url_prefix='/ml')

    from app.report import bp as report_bp
    app.register_blueprint(report_bp, url_prefix='/report')

    @app.route('/@vite/client')
    def vite_client_placeholder():
        # Some embedded dev browsers probe for Vite HMR even in non-Vite apps.
        # Returning an empty module keeps the page log clean during local testing.
        return Response('', mimetype='application/javascript')

    return app
