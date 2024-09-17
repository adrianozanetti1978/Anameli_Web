from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from coletor_dados_mlb import db
from werkzeug.security import check_password_hash
import json
from urllib.request import urlopen
from sqlalchemy.sql import text
from flask_login import login_user
from coletor_dados_mlb.models import NewUser

main = Blueprint('main', __name__)

# Rota para verificar a conexão com o banco de dados
@main.route('/check_db')
def check_db():
    try:
        # Tentativa de realizar uma operação simples no banco de dados
        db.session.execute(text('SELECT 1'))
        return "Conexão com o banco de dados bem-sucedida!", 200
    except Exception as e:
        return f"Erro ao conectar ao banco de dados: {e}", 500

# Rota para listar todos os usuários
@main.route('/users')
def list_users():
    try:
        users = NewUser.query.all()
        return render_template('users.html', users=users)
    except Exception as e:
        flash(f"Erro ao carregar os usuários: {e}", 'danger')
        return redirect(url_for('main.dashboard'))

@main.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = NewUser.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))

        else:
            flash('Usuário ou senha inválidos', 'danger')

    return render_template('login.html')

@main.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.login'))

@main.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        if request.method == 'POST':
            mlb_number = request.form.get('mlb_number')
            if mlb_number and mlb_number.isdigit():
                mlb_code = f"MLB{mlb_number}"
                dados, erro = carregar_dados(mlb_code)
                if dados:
                    resultados = criar_um_filtro(dados)
                    return render_template('resultados.html', resultados=resultados, mensagens_verificacao=resultados.get("Mensagens de Verificação", []))
                else:
                    flash(erro, 'danger')
            else:
                flash('Número inválido. Insira apenas números.', 'danger')

        return render_template('dashboard.html', username=session['username'])

    return redirect(url_for('main.login'))

# Funções auxiliares
def autenticar_usuario(username, password):
    user = NewUser.query.filter_by(username=username).first()
    if user:
        if check_password_hash(user.password_hash, password):
            return True, None
        else:
            return False, 'Nome de usuário ou senha incorretos'
    return False, 'Nome de usuário ou senha incorretos'

def carregar_dados(mlb_code):
    try:
        url = f"https://api.mercadolibre.com/items/{mlb_code}"
        response = urlopen(url).read().decode('utf8')
        return json.loads(response), None
    except Exception as e:
        return None, f"Erro ao carregar os dados: {e}"

def criar_um_filtro(dados):
    resultado = {}
    vendedor_endereco = dados.get("seller_address", {})
    resultado["Endereço do Vendedor"] = {
        "Cidade": vendedor_endereco.get("city", {}).get("name", "Não disponível"),
        "Estado": vendedor_endereco.get("state", {}).get("name", "Não disponível"),
        "País": vendedor_endereco.get("country", {}).get("name", "Não disponível")
    }
    pictures = dados.get("pictures", [])
    resultado["Número de fotos"] = len(pictures)

    if len(pictures) > 9:
        resultado["Fotos Válidas"] = True
        imagens_invalidas = []
        mensagens_verificacao = []

        for picture in pictures:
            size = picture.get('size', 'Não disponível')
            max_size = picture.get('max_size', 'Não disponível')
            mensagem = f"Verificando imagem com tamanho: {size} e max_size: {max_size}"
            mensagens_verificacao.append(mensagem)
            if size != "500x500" and size != "1200x1200":
                imagens_invalidas.append(picture.get('url'))

        resultado["Imagens com Resolução Incorreta"] = {
            "Count": len(imagens_invalidas),
            "URLs": imagens_invalidas
        }
        resultado["Mensagens de Verificação"] = mensagens_verificacao

    else:
        resultado["Fotos Válidas"] = False
        resultado["Imagens com Resolução Incorreta"] = "Menos de 10 fotos"

    video_ids = dados.get("video_ids", [])
    resultado["Vídeos Disponíveis"] = len(video_ids)
    if len(video_ids) > 0:
        resultado["Vídeos Válidos"] = True
        resultado["Video IDs"] = video_ids
    else:
        resultado["Vídeos Válidos"] = False

    tags_esperadas = [
        "extended_warranty_eligible",
        "good_quality_thumbnail",
        "immediate_payment",
        "cart_eligible"
    ]
    tags_presentes = dados.get("tags", [])
    tags_faltantes = [tag for tag in tags_esperadas if tag not in tags_presentes]
    tags_ativas = [tag for tag in tags_presentes if tag in tags_esperadas]

    resultado["Tags Faltantes"] = tags_faltantes
    resultado["Tags Ativas"] = tags_ativas

    return resultado
