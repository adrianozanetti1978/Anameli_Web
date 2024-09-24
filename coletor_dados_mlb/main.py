from flask import Blueprint, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Redireciona para a rota de login
    return redirect(url_for('auth.login'))