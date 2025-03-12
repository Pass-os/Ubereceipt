# main.py
from get_env import get_env

# Recupera o valor da variável MINHA_VARIAVEL
email = get_env("MY_EMAIL")
print("meu email é:", email)