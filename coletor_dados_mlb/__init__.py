from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from coletor_dados_mlb.config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from coletor_dados_mlb.routes import main
        app.register_blueprint(main)
        db.create_all()

    return app
