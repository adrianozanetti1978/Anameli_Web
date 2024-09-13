# config.py Heroku

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pefb5e67dfe258b22240c603af0d5af76547ef666398ed7352939fb6e7b352fd7')  
    # Substitua por uma chave secreta mais segura
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
    'postgresql://ucndp8ar8r14jk:pefb5e67dfe258b22240c603af0d5af76547ef666398ed7352939fb6e7b352fd7@cat670aihdrkt1.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/df3tf0rro1mmbn'
)

                                             
    SQLALCHEMY_TRACK_MODIFICATIONS = False