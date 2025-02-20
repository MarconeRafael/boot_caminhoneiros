import openai
from keys import chave_openai

openai.api_key = chave_openai  # Definindo a chave da API

def perguntar_proposta(message):
    try:
        # Histórico de conversa local (apenas dessa interação)
        conversation_history = [
            {"sender": "user", "content": "Qual é a sua proposta?"}
        ]

        # Formatação do histórico de conversa
        mensagens = [{"role": "system", "content": "Você é um assistente inteligente."}]
        for msg in conversation_history:
            role = "user" if msg.get('sender') == 'user' else "assistant"
            mensagens.append({"role": role, "content": msg['content']})

        # Enviando uma solicitação para o modelo gpt-3.5-turbo
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Usando o modelo mais barato
            messages=mensagens,
            max_tokens=150  # Defina o número máximo de tokens para a resposta
        )

        # Obtendo a resposta gerada
        proposta = response['choices'][0]['message']['content']

        # Responde com a proposta ao usuário
        message.reply(f"A proposta recebida é: {proposta}")
        return proposta

    except Exception as e:
        print(f"Erro ao obter a proposta: {e}")
        message.reply("Houve um erro ao obter a proposta.")
        return None


