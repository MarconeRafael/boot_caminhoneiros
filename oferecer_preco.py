import openai
from keys import chave_openai

openai.api_key = chave_openai  # Definindo a chave da API

def oferecer_preco(preco_frete):
    """
    Gera um prompt para oferecer um preço de frete ao usuário.
    """
    return f"O preço do frete é R$ {preco_frete:.2f}. Você aceita?"
