import openai
from keys import chave_openai

openai.api_key = chave_openai  # Definindo a chave da API

def perguntar_proposta():
    """
    Retorna uma mensagem solicitando a proposta do usuário.
    """
    return "💡 Qual valor você propõe?"
