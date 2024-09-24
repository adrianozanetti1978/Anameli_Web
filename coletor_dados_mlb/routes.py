from flask import Blueprint, render_template


# Definindo o Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Rota para a página inicial"""
    return render_template('templates/login.html')

# Tratamento de erros - 404
@main_bp.app_errorhandler(404)
def page_not_found(e):
    """Rota para a página de erro 404"""
    return render_template('404.html'), 404

# Tratamento de erros - 500 (opcional)
@main_bp.app_errorhandler(500)
def internal_server_error(e):
    """Rota para a página de erro 500"""
    return render_template('500.html'), 500
