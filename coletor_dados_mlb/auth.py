from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
from . import db
from .models import NewUser

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = NewUser.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            current_app.logger.info(f'Usuário {username} fez login com sucesso.')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Usuário ou senha inválidos.', 'error')
            current_app.logger.warning(f'Tentativa de login falhada para o usuário {username}.')

    return render_template('login.html')

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    username = request.form.get('username')
    logout_user()
    flash('Você foi desconectado.', 'info')
    current_app.logger.info(f'Usuário {username} desconectado.')
    return redirect(url_for('auth.login'))