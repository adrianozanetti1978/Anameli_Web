# __init__.py Heroku

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from urllib.parse import urlparse

# Inicialização do SQLAlchemy e Flask-Migrate
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder='templates')  # Especifica o diretório de templates e estático
    
    # Configuração do banco de dados
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("Variável de ambiente 'DATABASE_URL' não está definida.")
    
    parsed_url = urlparse(database_url)
    db_user = parsed_url.username
    db_password = parsed_url.password
    db_host = parsed_url.hostname
    db_port = parsed_url.port
    db_name = parsed_url.path[1:]  # Remove a barra inicial
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Opcional: desativa o rastreamento de modificações para melhorar o desempenho
    
    # Carrega a configuração do config.py
    app.config.from_object('config.Config')

    db.init_app(app)  # Inicializa o SQLAlchemy com a aplicação
    migrate.init_app(app, db)

    with app.app_context():
        # Registrar Blueprints
        from application.routes import main
        app.register_blueprint(main)

        # Criação de tabelas e inicialização do banco de dados
        from application.models import Account, NewAccount  # Agora inclui o NewAccount
        db.create_all()  # Cria todas as tabelas

    return app
