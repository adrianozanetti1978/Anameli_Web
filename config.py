# config.py Heroku

import os

class Config:
    # Use uma chave secreta mais segura em produção
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pefb5e67dfe258b22240c603af0d5af76547ef666398ed7352939fb6e7b352fd7')  
    
    # Obtém a URL do banco de dados a partir das variáveis de ambiente
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Substitui 'postgres://' por 'postgresql://' no URI para compatibilidade com SQLAlchemy
    SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql://') if DATABASE_URL else 'postgresql://ucndp8ar8r14jk:pefb5e67dfe258b22240c603af0d5af76547ef666398ed7352939fb6e7b352fd7@cat670aihdrkt1.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/df3tf0rro1mmbn'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
