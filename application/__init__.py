# __init__.py (ou create_app)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=None):
    app = Flask(__name__, template_folder='templates')
    
    if config_class:
        app.config.from_object(config_class)
    else:
        app.config.from_object('application.config.Config')  # Padrão

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from application.routes import main
        app.register_blueprint(main)

        from application.models import Account, NewAccount
        db.create_all()

    return app
