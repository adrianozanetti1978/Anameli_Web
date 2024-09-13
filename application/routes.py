# routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, send_file
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
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.login'))

@main.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Cria nova conta na tabela NewAccount
        new_account = NewAccount(username=username, email=email, is_active=True)
        new_account.set_password(password)
        db.session.add(new_account)
        db.session.commit()
        
        # Armazena a mensagem de sucesso na sessão
        session['message'] = 'Usuário cadastrado com sucesso!'
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
                flash("Usuário bloqueado com sucesso.", 'message')
            elif action == 'unblock':
                user.is_active = True
                flash("Usuário desbloqueado com sucesso.", 'message')
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

    print(f"User ID recebido: {user_id}")  # Adicione esta linha para depuração
    user = None
    if user_id:
        user = NewAccount.query.get_or_404(user_id)

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        print(f"User ID do formulário: {user_id}")  # Adicione esta linha para depuração
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
    # Informações do banco de dados (extraídas da classe Config)
    db_user = 'postgres'
    db_password = '238779Adri'
    db_host = 'localhost'
    db_port = '5432'
    db_name = 'usuario_db'

    # Verifique se todas as variáveis de ambiente estão definidas
    if not all([db_user, db_password, db_host, db_port, db_name]):
        return "Erro: Falta configuração de uma ou mais variáveis de ambiente.", 500

    # Defina o nome do arquivo temporário
    backup_file = tempfile.NamedTemporaryFile(delete=False, suffix='.sql')

    # Comando para realizar o backup do banco de dados
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

    # Define a variável de ambiente PGPASSWORD para evitar solicitar a senha interativamente
    os.environ['PGPASSWORD'] = db_password

    try:
        # Execute o comando de backup
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        return f"Erro ao criar backup: {e}", 500
    finally:
        # Limpar a variável de ambiente PGPASSWORD
        del os.environ['PGPASSWORD']

    # Enviar o arquivo para o cliente
    response = send_file(
        backup_file.name,
        as_attachment=True,
        download_name='backup.sql'  # Nome do arquivo de download
    )

    # Remover o arquivo temporário após o envio
    @response.call_on_close
    def cleanup():
        os.remove(backup_file.name)

    return response