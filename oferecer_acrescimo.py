import openai
from keys import chave_openai

openai.api_key = chave_openai  # Definindo a chave da API

def oferecer_acrescimo(preco_frete):
    """
    Retorna apenas o prompt da oferta de frete com acréscimo de 10%.
    """
    preco_acrescido = preco_frete * 1.10  # Aplicando 10% de acréscimo
    return (
        f"O preço original do frete era R$ {preco_frete:.2f}. "
        f"Podemos oferecer um acréscimo de 10%, totalizando R$ {preco_acrescido:.2f}. Você aceita?"
    )
