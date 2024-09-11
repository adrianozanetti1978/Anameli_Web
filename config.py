import os

class Config:
    SECRET_KEY = '238779Adri'  # Altere para uma chave secreta real
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:238779Adri@localhost:5432/usuario_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False