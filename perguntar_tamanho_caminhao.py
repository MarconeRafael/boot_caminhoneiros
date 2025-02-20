import openai
from keys import chave_openai

openai.api_key = chave_openai  # Definindo a chave da API

def perguntar_tamanho_caminhao(message):
    """
    Verifica e extrai, usando a API GPT, as informações sobre tipo de caminhão, comprimento e altura.
    Responde ao usuário utilizando message.reply().
    """
    # Histórico de conversa local (apenas dessa interação)
    conversation_history = [
        {"sender": "user", "content": "Qual o tamanho do caminhão necessário para esse frete?"},
        {"sender": "assistant", "content": "Qual o tipo de caminhão você prefere? Aberto ou fechado?"},
        {"sender": "user", "content": "Eu preciso de um caminhão fechado."},
        {"sender": "assistant", "content": "Qual é o comprimento e a altura do caminhão?"}
    ]

    # Formatação do histórico de conversa
    mensagens = [{"role": "system", "content": "Você é um assistente útil."}]
    for msg in conversation_history:
        role = "user" if msg.get('sender') == 'user' else "assistant"
        mensagens.append({"role": role, "content": msg['content']})

    # Pergunta ao modelo para extrair as informações
    pergunta = (
        "Com base no histórico de conversa, extraia as seguintes informações e retorne-as de forma estruturada:\n"
        "1. Tipo do caminhão\n aberto/fechado\n"
        "2. Comprimento do caminhão (em metros)\n"
        "3. Altura do caminhão (em metros)\n"
        "Se alguma informação não estiver presente, responda com 'Não fornecido'."
    )
    mensagens.append({"role": "user", "content": pergunta})

    try:
        # Chamada para a API GPT
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Modelo mais barato
            messages=mensagens
        )

        mensagem_resposta = resposta['choices'][0]['message']['content']

        # Processa a resposta do modelo
        tipo_caminhao = None
        comprimento_caminhao = None
        altura_caminhao = None

        # Tenta extrair as informações da resposta do modelo
        linhas = mensagem_resposta.split("\n")
        for linha in linhas:
            if "tipo do caminhão" in linha.lower():
                tipo_caminhao = linha.split(":")[1].strip() if ":" in linha else "Não fornecido"
            elif "comprimento" in linha.lower():
                comprimento_caminhao = linha.split(":")[1].strip() if ":" in linha else "Não fornecido"
            elif "altura" in linha.lower():
                altura_caminhao = linha.split(":")[1].strip() if ":" in linha else "Não fornecido"

        # Calcula o volume se possível
        try:
            volume = float(comprimento_caminhao) * float(altura_caminhao) * 2.5
        except ValueError:
            volume = "Não pode ser calculado"

        # Responde ao usuário com a mensagem de volume
        message.reply(f"Tipo do caminhão: {tipo_caminhao}\n"
                      f"Comprimento do caminhão: {comprimento_caminhao} metros\n"
                      f"Altura do caminhão: {altura_caminhao} metros\n"
                      f"Volume estimado: {volume} m³")

    except openai.error.OpenAIError as e:
        message.reply("Erro ao processar a solicitação. Tente novamente mais tarde.")
