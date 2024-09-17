from dotenv import load_dotenv
import os

load_dotenv()  # Carrega variáveis de ambiente do arquivo .env

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pefb5e67dfe258b22240c603af0d5af76547ef666398ed7352939fb6e7b352fd7')  
    DATABASE_URL = os.environ.get('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql://') if DATABASE_URL else None
    
    if SQLALCHEMY_DATABASE_URI is None:
        SQLALCHEMY_DATABASE_URI = 'postgresql://ucndp8ar8r14jk:pefb5e67dfe258b22240c603af0d5af76547ef666398ed7352939fb6e7b352fd7@cat670aihdrkt1.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/df3tf0rro1mmbn'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
