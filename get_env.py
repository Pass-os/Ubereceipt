import os
from dotenv import load_dotenv

# Carrega as variáveis definidas no arquivo .env
load_dotenv()

# Recupera o valor da variável MINHA_VARIAVEL
minha_variavel = os.getenv("IMAP_KEY")

def get_env(var_name):
    """Retorna o valor da variável de ambiente especificada."""
    return os.getenv(var_name)