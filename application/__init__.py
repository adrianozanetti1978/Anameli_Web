from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder='templates')  # Especifica o diretório de templates e estático
    app.config.from_object('config.Config')  # Carrega a configuração do config.py

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Registrar Blueprints
        from application.routes import main
        app.register_blueprint(main)

        # Criação de tabelas e inicialização do banco de dados
        from application.models import Account, NewAccount  # Agora inclui o NewAccount
        db.create_all()

    return app

# Exporta a instância da aplicação
app = create_app()
