import openai
from keys import chave_openai

openai.api_key = chave_openai  # Definindo a chave da API

def perguntar_tamanho_caminhao():
    """
    Retorna uma mensagem solicitando informações sobre o caminhão necessário.
    """
    return (
        "🚛 Para calcular o tamanho do caminhão necessário, preciso saber:\n"
        "1️⃣ O caminhão deve ser aberto ou fechado?\n"
        "2️⃣ Qual o comprimento estimado (em metros)?\n"
        "3️⃣ Qual a altura estimada (em metros)?"
    )
