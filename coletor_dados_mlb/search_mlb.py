# search_mlb.py

import json
import logging
from urllib.request import urlopen
from flask import Blueprint, jsonify, request

# Configurando o logger
logger = logging.getLogger(__name__)

# Definindo o Blueprint
search_mlb_bp = Blueprint('search_mlb', __name__)

def carregar_dados(mlb_code):
    try:
        url = f"https://api.mercadolibre.com/items/{mlb_code}"
        logger.info(f"Carregando dados do URL: {url}")
        response = urlopen(url).read().decode('utf8')
        return json.loads(response), None
    except Exception as e:
        logger.error(f"Erro ao carregar os dados do URL {url}: {e}", exc_info=True)
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

    return resultado

# Rota de exemplo para testar o carregamento de dados
@search_mlb_bp.route('/search/<string:mlb_code>', methods=['GET'])
def search(mlb_code):
    dados, erro = carregar_dados(mlb_code)
    if erro:
        return jsonify({"error": erro}), 500
    resultado = criar_um_filtro(dados)
    return jsonify(resultado)
