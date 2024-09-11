from werkzeug.security import generate_password_hash

def create_password_hash():
    """Função para gerar o hash da senha a partir de uma entrada do usuário."""
    password = input("Digite a senha que deseja converter para hash: ")
    # Especifica o algoritmo pbkdf2:sha256
    password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    return password_hash

# Exemplo de uso:
hash_senha = create_password_hash()
print(f"Hash da senha gerado: {hash_senha}")