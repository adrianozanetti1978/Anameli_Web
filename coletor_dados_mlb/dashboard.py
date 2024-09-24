# dashboard.py

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required
from . import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    from .models import SomeModel
    # Renderiza a página do dashboard para o usuário autenticado
    return render_template('dashboard.html')

# Mova a função search_mlb.py para o arquivo search_mlb.py
# Remova a função search_mlb daqui
