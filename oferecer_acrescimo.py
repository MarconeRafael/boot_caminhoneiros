import openai
from keys import chave_openai

openai.api_key = chave_openai  # Definindo a chave da API

def oferecer_acrescimo(preco_frete, message):
    """
    Utiliza a API da OpenAI para formular uma oferta de frete com um acréscimo de 10%.
    """
    preco_acrescido = preco_frete * 1.10  # Aplicando 10% de acréscimo
    mensagem = (
        f"O preço original do frete era R$ {preco_frete:.2f}. "
        f"Podemos oferecer um acréscimo de 10%, totalizando R$ {preco_acrescido:.2f}. Você aceita?"
    )

    # Chamando a API para gerar a resposta
    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Modelo mais barato
        messages=[{"role": "system", "content": "Você é um assistente comercial."},
                  {"role": "user", "content": mensagem}]
    )

    # Responde ao usuário com a oferta gerada
    message.reply(resposta['choices'][0]['message']['content'])

    return resposta['choices'][0]['message']['content'], preco_acrescido
