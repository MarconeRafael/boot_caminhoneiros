import openai
import json
import re
import sys
import os

from keys import chave_openai, numero_destino1
from transcrever_audio import transcrever_audio
from perguntar_tamanho_caminhao import perguntar_tamanho_caminhao
from verificar_capacidade import verificar_capacidade
from oferecer_preco import oferecer_preco
from oferecer_acrescimo import oferecer_acrescimo
from perguntar_proposta import perguntar_proposta
from tchau_caminhoneiro import tchau_caminhoneiro
from fretes import carregar_fretes

# Carregar os dados dos fretes
fretes_df, fretes_dict, lista_fretes_str = carregar_fretes(caminho_arquivo="data/xls/fretes.xlsx")

# Configuração da chave da API do OpenAI
openai.api_key = chave_openai

def chat_with_gpt(prompt, conversation_history, system_message):
    """
    Envia o prompt (junto com o histórico de conversa) para o GPT e retorna a resposta.
    """
    base_system_message = (
        f"Use mensagens curtas pois caminhoneiros gostam. Você é um atendente simpático "
        f"que conversa de maneira clara e amigável com caminhoneiros a fim de contratar o serviço de fretes deles. "
        f"Temos os fretes disponíveis:\n{lista_fretes_str}\n"
        f"Não invente dados e forneça as informações necessárias de forma bem formatada. "
        f"Saiba que você tem cargas de telhas e deseja contratar caminhoneiros para realizar os fretes. "
        f"Os caminhoneiros estão conversando com você."
    )
    full_system_message = f"{base_system_message} {system_message}" if system_message else base_system_message

    conversation_history.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": full_system_message}] + conversation_history
    )
    reply = response.choices[0].message['content']
    conversation_history.append({"role": "assistant", "content": reply})
    print(reply)
    return reply

def classificar_resposta(resposta, historico_conversa):
    """
    Classifica a resposta do caminhoneiro usando o GPT.
    Retorna: "aceito", "negociacao" ou "rejeicao".
    """
    prompt = f"""
        Você é um assistente que analisa respostas de caminhoneiros.
        Dada a resposta abaixo, classifique-a em uma das seguintes categorias e responda apenas uma palavra:
        - "aceito": se o caminhoneiro aceitou a oferta.
        - "negociacao": se o caminhoneiro quer negociar ou sugeriu uma contra-oferta.
        - "rejeicao": se o caminhoneiro rejeitou a oferta.

        Responda apenas com uma dessas palavras.

        Resposta: "{resposta}"
    """
    classificacao = chat_with_gpt(prompt, historico_conversa, "Analisando a resposta do caminhoneiro.")
    return classificacao.strip().lower()

def limpar_localidade(localidade):
    """
    Remove caracteres especiais como '/', '-' e converte para maiúsculo.
    Se a localidade for None, retorna uma string vazia.
    """
    if localidade is None:
        return ""
    return re.sub(r"[\s\-\/]", "", str(localidade)).upper()


def extrair_destino_origem_gpt(mensagem):
    """
    Usa a API do GPT para extrair as informações de destino e origem
    da mensagem, retornando um dicionário com as chaves "destino" e "origem".
    """
    prompt = f"""
        Extraia as informações de destino e origem do seguinte texto.
        Retorne apenas um JSON com as chaves "destino" e "origem".
        Texto: "{mensagem}"
    """
    response = openai.ChatCompletion.create(
       model="gpt-3.5-turbo",
       messages=[
           {"role": "system", "content": "Você é um assistente que extrai informações de fretes."},
           {"role": "user", "content": prompt}
       ]
    )
    
    result_str = response['choices'][0]['message']['content']
    
    try:
        result_json = json.loads(result_str)
    except json.JSONDecodeError:
        result_json = {}
    
    return result_json

def verificar_comparacao_com_api(destino, origem, fretes_df):
    """
    Usa a API do GPT para comparar a origem e o destino extraídos com os registros
    disponíveis e retorna se há correspondência.
    """
    fretes_lista = fretes_df[['Destino', 'Origem']].apply(lambda row: f"Destino: {row['Destino']}, Origem: {row['Origem']}", axis=1).tolist()
    fretes_texto = "\n".join(fretes_lista)

    prompt = f"""
        Verifique se a origem e o destino extraídos da mensagem correspondem a algum dos registros abaixo,
        mesmo que escritos de forma diferente, mas se referindo ao mesmo lugar:
        Destino: {destino}, Origem: {origem}
        
        Registros de frete disponíveis:
        {fretes_texto}

        Responda apenas com "sim" se houver correspondência ou "não" se não houver.
    """
    
    response = openai.ChatCompletion.create(
       model="gpt-3.5-turbo",
       messages=[
           {"role": "system", "content": "Você é um assistente que verifica correspondência entre registros."},
           {"role": "user", "content": prompt}
       ]
    )
    
    result_str = response['choices'][0]['message']['content'].strip().lower()
    
    return result_str == "sim"

def selecionar_frete(mensagem, fretes_df):
    destino_pattern = r"destino\s*[:\-]\s*([A-Za-z\s]+)"
    origem_pattern  = r"origem\s*[:\-]\s*([A-Za-z\s]+)"
    
    destino_match = re.search(destino_pattern, mensagem, re.IGNORECASE)
    origem_match  = re.search(origem_pattern, mensagem, re.IGNORECASE)
    
    if destino_match and origem_match:
        destino = destino_match.group(1).strip().upper()
        origem  = origem_match.group(1).strip().upper()
    else:
        extraido = extrair_destino_origem_gpt(mensagem)
        destino = extraido.get("destino", "")
        origem  = extraido.get("origem", "")

    destino = limpar_localidade(destino)
    origem = limpar_localidade(origem)
    
    if verificar_comparacao_com_api(destino, origem, fretes_df):
        fretes_filtrados = fretes_df[
            (fretes_df['Destino'].str.upper().apply(limpar_localidade) == destino) &
            (fretes_df['Origem'].str.upper().apply(limpar_localidade) == origem)
        ]
        if not fretes_filtrados.empty:
            return fretes_filtrados.iloc[0]
    
    return None

def encaminhar_contato_local(preco_frete, destino_frete, numero_destino):
    """
    Envia as informações do frete via WhatsApp para o número de destino.
    Neste exemplo, a mensagem é exibida via print.
    """
    try:
        preco_frete_num = float(preco_frete)
    except ValueError:
        preco_frete_num = 0.0

    mensagem = (
        f"Detalhes do Frete:\n"
        f"📍 Destino: {destino_frete}\n"
        f"💰 Preço do Frete: R$ {preco_frete_num:.2f}"
    )
    
    print("Enviando mensagem para", numero_destino)
    print(mensagem)
    
    return mensagem

def fluxo(historico_conversa, frete_selecionado):
    """
    Executa o fluxo de negociação com o caminhoneiro a partir do frete selecionado.
    """
    numero_destino = numero_destino1

    volume_frete  = frete_selecionado['Carga']
    preco_frete   = frete_selecionado['Preço']
    destino_frete = frete_selecionado['Destino']

    system_msg = perguntar_tamanho_caminhao()
    system_msg += f" | Frete: Destino {destino_frete}, Carga {volume_frete}, Preço R$ {preco_frete}"
    chat_with_gpt("Qual o tamanho do seu caminhão?", historico_conversa, system_msg)
    
    tamanho_caminhao = input()
    historico_conversa.append({"role": "user", "content": tamanho_caminhao})

    caber = verificar_capacidade(volume_frete, tamanho_caminhao)
    
    if caber:
        system_msg = oferecer_preco(preco_frete)
        chat_with_gpt(f"Ofereço o frete por R$ {preco_frete}. Você aceita?", historico_conversa, system_msg)
        resposta_preco = input()
        historico_conversa.append({"role": "user", "content": resposta_preco})
        classificacao_preco = classificar_resposta(resposta_preco, historico_conversa)
        if classificacao_preco == "aceito":
            system_msg = encaminhar_contato_local(preco_frete, destino_frete, numero_destino)
            chat_with_gpt("Encaminhando contato e informações do frete.", historico_conversa, system_msg)
            sys.exit(0)  # Finaliza o programa aqui

        elif classificacao_preco == "negociacao":
            novo_preco = preco_frete * 1.10  # Acréscimo de 10%
            system_msg = oferecer_acrescimo(novo_preco)
            chat_with_gpt(f"Posso ajustar para R$ {novo_preco}? Você aceita?", historico_conversa, system_msg)
            resposta_acrescimo = input()
            historico_conversa.append({"role": "user", "content": resposta_acrescimo})
            classificacao_acrescimo = classificar_resposta(resposta_acrescimo, historico_conversa)
            
            if classificacao_acrescimo == "aceito":
                system_msg = encaminhar_contato_local(novo_preco, destino_frete, numero_destino)
                chat_with_gpt("Encaminhando contato e informações com o novo preço.", historico_conversa, system_msg)
                sys.exit(0)  # Finaliza o programa aqui

            else:
                system_msg = perguntar_proposta()
                chat_with_gpt("Qual a sua proposta?", historico_conversa, system_msg)
                proposta = input()
                historico_conversa.append({"role": "user", "content": proposta})
                system_msg = encaminhar_contato_local(proposta, destino_frete, numero_destino)
                chat_with_gpt("Encaminhando contato e informações do frete com sua proposta.", historico_conversa, system_msg)
        elif classificacao_preco == "rejeicao":
            system_msg = tchau_caminhoneiro(False)
            chat_with_gpt("Obrigado, até a próxima!", historico_conversa, system_msg)
            sys.exit(1)
        else:
            system_msg = tchau_caminhoneiro(False)
            chat_with_gpt("Obrigado, até a próxima!", historico_conversa, system_msg)
            sys.exit(1)
    else:
        system_msg = tchau_caminhoneiro(False)
        chat_with_gpt("Infelizmente, seu caminhão não comporta este frete. Obrigado!", historico_conversa, system_msg)
        sys.exit(1)

def main():

    
    historico_conversa = []

    if len(sys.argv) < 2:
        print("Por favor, forneça um arquivo de áudio ou um prompt de texto.")
        sys.exit(1)

    input_data = sys.argv[1]

    if os.path.isfile(input_data):
        file_extension = os.path.splitext(input_data)[1].lower()
        if file_extension == '.ogg':
            prompt = transcrever_audio(input_data, "Transcrevendo áudio...")
        else:
            print(f"Formato de arquivo '{file_extension}' não suportado para transcrição.")
            sys.exit(1)
    else:
        prompt = input_data

    # Seleciona o frete com base no destino e origem informados na mensagem
    frete_selecionado = selecionar_frete(prompt, fretes_df)
    if frete_selecionado is None:
        chat_with_gpt(prompt, historico_conversa, "Nenhum frete encontrado com as características informadas na mensagem.")
        sys.exit(1)

    # Inicia o fluxo com o frete selecionado
    fluxo(historico_conversa, frete_selecionado)

    # Processa a mensagem final (se houver)
    chat_with_gpt(prompt, historico_conversa, "Processando sua solicitação final.")

if __name__ == "__main__":
    main()
