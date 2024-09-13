from flask import Blueprint, render_template, redirect, url_for, request, flash, session, send_file, current_app as app, jsonify
from . import db
from application.models import Account, NewAccount  # Importação de Account e NewAccount
import os
import subprocess
import tempfile

main = Blueprint('main', __name__)


@main.route('/')
def home():
    return redirect(url_for('main.login'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Busca o usuário na tabela Account (autenticação)
        account = Account.query.filter_by(username=username).first()

        # Verifica se o usuário existe e se a senha está correta
        if account and account.check_password(password):
            # Salva o nome de usuário na sessão para manter o estado de login
            session['username'] = username
            return redirect(url_for('main.dashboard'))  # Redireciona para o dashboard
        else:
            flash('Usuário ou senha inválidos', 'error')

    return render_template('login.html')


@main.route('/dashboard')
def dashboard():
    # Verifica se o usuário está logado
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('main.login'))


@main.route('/logout', methods=['POST'])
def logout():
    # Remove o usuário da sessão para deslogar
    session.pop('username', None)
    
    # Verifica se é uma solicitação AJAX (usada para logout ao fechar a aba)
    if request.is_json:  # ou use request.is_xhr, dependendo da versão do Flask
        # Retorna uma resposta JSON
        return jsonify({'status': 'success', 'message': 'Você foi desconectado.'})
    else:
        # Se não for uma requisição AJAX, continua o fluxo normal de logout
        flash('Você foi desconectado.', 'info')
        return redirect(url_for('main.login'))


@main.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Verifica se as senhas coincidem
        if password != confirm_password:
            flash('As senhas não coincidem. Tente novamente.', 'error')
            return redirect(url_for('main.cadastrar_usuario'))

        # Cria nova conta na tabela NewAccount
        new_account = NewAccount(username=username, email=email, is_active=True)
        new_account.set_password(password)
        db.session.add(new_account)
        db.session.commit()
        
        # Armazena a mensagem de sucesso na sessão
        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('main.cadastrar_usuario'))

    # Recupera a mensagem da sessão
    message = session.pop('message', None)
    return render_template('cadastrar.html', message=message)


@main.route('/editar', methods=['GET', 'POST'])
def editar_usuario():
    search_query = request.args.get('search', '')
    user_id = request.args.get('user_id')

    if user_id:
        user = NewAccount.query.get_or_404(user_id)
    else:
        user = None

    if request.method == 'POST':
        if user:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            if password and password != confirm_password:
                flash('As senhas não coincidem!', 'error')
                return redirect(url_for('main.editar_usuario', user_id=user.id, search=search_query))

            user.username = username
            user.email = email

            if password:
                user.set_password(password)

            db.session.commit()  # Certifica-se de que as alterações estão sendo salvas

            # Adiciona mensagem de sucesso
            flash('Usuário atualizado com sucesso!', 'success')

            return redirect(url_for('main.editar_usuario', user_id=user.id, search=search_query))

    users = NewAccount.query.filter(NewAccount.username.like(f'%{search_query}%')).all() if search_query else NewAccount.query.all()

    return render_template('editar.html', user=user, users=users, search_query=search_query, selected_user_id=user_id)


@main.route('/bloquear', methods=['GET', 'POST'])
def bloquear_usuario():
    search_query = request.args.get('search', '')  # Obtém a consulta de pesquisa, se existir
    
    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')

        if not user_id:
            flash("Por favor, selecione um usuário.", 'error')
            return redirect(url_for('main.bloquear_usuario', search=search_query))

        user = NewAccount.query.get(user_id)
        if user:
            if action == 'block':
                user.is_active = False
                flash("Usuário bloqueado com sucesso.", 'success')
            elif action == 'unblock':
                user.is_active = True
                flash("Usuário desbloqueado com sucesso.", 'success')
            db.session.commit()
        else:
            flash("Usuário não encontrado.", 'error')

        return redirect(url_for('main.bloquear_usuario', search=search_query))
    
    # Aplica o filtro de pesquisa
    users_query = NewAccount.query
    if search_query:
        users_query = users_query.filter(
            NewAccount.username.ilike(f'%{search_query}%') | 
            NewAccount.email.ilike(f'%{search_query}%')
        )
    users = users_query.all()
    
    return render_template('bloquear.html', users=users, search_query=search_query)


@main.route('/excluir', methods=['GET', 'POST'])
def excluir_usuario():
    search_query = request.args.get('search', '')
    user_id = request.args.get('user_id')


    user = None
    if user_id:
        user = NewAccount.query.get_or_404(user_id)

    if request.method == 'POST':
        user_id = request.form.get('user_id')

        if user_id:
            user = NewAccount.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                flash('Usuário excluído com sucesso!', 'success')
            else:
                flash('Usuário não encontrado!', 'error')
        else:
            flash('ID do usuário não fornecido!', 'error')
        return redirect(url_for('main.excluir_usuario', search=search_query))

    users_query = NewAccount.query
    if search_query:
        users_query = users_query.filter(NewAccount.username.like(f'%{search_query}%'))
    users = users_query.all()

    return render_template('excluir.html', users=users, search_query=search_query, selected_user_id=user_id)


@main.route('/backup')
def backup():
    db_user = os.environ.get('DB_USER', 'ucndp8ar8r14jk')
    db_password = os.environ.get('DB_PASSWORD', 'pefb5e67dfe258b22240c603af0d5af76547ef666398ed7352939fb6e7b352fd7')
    db_host = os.environ.get('DB_HOST', 'cat670aihdrkt1.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'df3tf0rro1mmbn')

    # Adicionar logs de depuração
    app.logger.debug(f"DB_USER: {db_user}")
    app.logger.debug(f"DB_HOST: {db_host}")
    app.logger.debug(f"DB_NAME: {db_name}")

    if not all([db_user, db_password, db_host, db_port, db_name]):
        app.logger.error("Falta configuração de uma ou mais variáveis de ambiente.")
        return "Erro: Falta configuração de uma ou mais variáveis de ambiente.", 500

    backup_file = tempfile.NamedTemporaryFile(delete=False, suffix='.sql')

    command = [
        'pg_dump',
        '-U', db_user,
        '-h', db_host,
        '-p', db_port,
        '-F', 'c',
        '--file', backup_file.name,
        '--compress', '9',
        db_name
    ]

    os.environ['PGPASSWORD'] = db_password

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Erro ao criar backup: {e}")
        return f"Erro ao criar backup: {e}", 500
    finally:
        if 'PGPASSWORD' in os.environ:
            del os.environ['PGPASSWORD']

    response = send_file(
        backup_file.name,
        as_attachment=True,
        download_name='backup.sql'
    )

    @response.call_on_close
    def cleanup():
        os.remove(backup_file.name)

    return response