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

# Caminho para o arquivo que armazena o histórico de conversa
HISTORY_FILE = "conversation_history.json"

def load_conversation_history():
    """Carrega o histórico de conversa a partir do arquivo, se existir."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print("Erro ao carregar histórico:", e)
    return []

def save_conversation_history(history):
    """Salva o histórico de conversa no arquivo."""
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f)
    except Exception as e:
        print("Erro ao salvar histórico:", e)

def chat_with_gpt(prompt, conversation_history, system_message=""):
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

    # Adiciona a mensagem do usuário ao histórico
    conversation_history.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": full_system_message}] + conversation_history
    )
    reply = response.choices[0].message['content']
    # Adiciona a resposta do assistente ao histórico
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
    result = classificacao.strip().lower()
    print("Classificação:", result)
    return result

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
    Usa a API do GPT para extrair as informações de destino e origem da mensagem,
    retornando um dicionário com as chaves "destino" e "origem".
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
    Compara a origem e o destino extraídos com os registros disponíveis.
    Retorna True se houver correspondência.
    """
    fretes_lista = fretes_df[['Destino', 'Origem']].apply(
        lambda row: f"Destino: {row['Destino']}, Origem: {row['Origem']}", axis=1
    ).tolist()
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
    """
    Seleciona o frete com base em seleção numérica ou extração de destino/origem.
    """
    # Primeiro verifica se é uma seleção numérica
    if mensagem.strip().isdigit():
        try:
            index = int(mensagem.strip()) - 1  # Converte para índice 0-based
            if 0 <= index < len(fretes_df):
                return fretes_df.iloc[index]
            else:
                return None
        except:
            return None
    
    # Se não for número, prossegue com extração de localidades
    destino_pattern = r"destino\s*[:\-]\s*([A-Za-z\s]+)"
    origem_pattern  = r"origem\s*[:\-]\s*([A-Za-z\s]+)"
    
    destino_match = re.search(destino_pattern, mensagem, re.IGNORECASE)
    origem_match  = re.search(origem_pattern, mensagem, re.IGNORECASE)
    
    if destino_match and origem_match:
        destino = destino_match.group(1).strip().upper()
        origem = origem_match.group(1).strip().upper()
    else:
        extraido = extrair_destino_origem_gpt(mensagem)
        destino = extraido.get("destino", "")
        origem = extraido.get("origem", "")
    
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
    Prepara e exibe a mensagem de encaminhamento do frete (simula envio via WhatsApp).
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

def perguntar_usuario(pergunta, historico_conversa, system_msg=""):
    """
    Envia uma mensagem ao usuário via GPT e capta a resposta.
    """
    chat_with_gpt(pergunta, historico_conversa, system_msg)
    resposta = input("Sua resposta: ")
    historico_conversa.append({"role": "user", "content": resposta})
    return resposta

def negociar_preco(preco_frete, historico_conversa):
    """
    Executa o fluxo de negociação de preço.
    Retorna uma tupla (status, valor) onde:
      - status pode ser "aceito", "aceito_com_acrescimo", "proposta" ou "rejeicao"
      - valor é o preço final ou a proposta do caminhoneiro.
    """
    resposta_preco = perguntar_usuario(
        f"Ofereço o frete por R$ {preco_frete}. Você aceita?",
        historico_conversa,
        oferecer_preco(preco_frete)
    )
    classificacao_preco = classificar_resposta(resposta_preco, historico_conversa)
    
    if classificacao_preco == "aceito":
        return "aceito", preco_frete
    elif classificacao_preco == "negociacao":
        novo_preco = preco_frete * 1.10  # Acréscimo de 10%
        resposta_acrescimo = perguntar_usuario(
            f"Posso ajustar para R$ {novo_preco}? Você aceita?",
            historico_conversa,
            oferecer_acrescimo(novo_preco)
        )
        classificacao_acrescimo = classificar_resposta(resposta_acrescimo, historico_conversa)
        if classificacao_acrescimo == "aceito":
            return "aceito_com_acrescimo", novo_preco
        else:
            proposta = perguntar_usuario(
                "Qual a sua proposta?",
                historico_conversa,
                perguntar_proposta()
            )
            return "proposta", proposta
    else:
        return "rejeicao", None

# --- Fluxo de negociação quebrado em funções menores ---

def inicializar_parametros_negociacao(frete_selecionado):
    """
    Inicializa os parâmetros da negociação com base no frete selecionado.
    """
    numero_destino = numero_destino1
    preco_frete = frete_selecionado['Preço']
    origem_frete = frete_selecionado['Origem']
    destino_frete = frete_selecionado['Destino']
    return numero_destino, preco_frete, origem_frete, destino_frete

def obter_tamanho_caminhao(historico_conversa):
    """
    Pergunta e retorna o tamanho do caminhão informado pelo usuário.
    """
    # Utiliza apenas uma chamada a perguntar_usuario para coletar o tamanho do caminhão
    tamanho = perguntar_usuario("Qual o tamanho do seu caminhão?", historico_conversa, perguntar_tamanho_caminhao())
    return tamanho

def processar_capacidade(tamanho_caminhao, historico_conversa):
    """
    Nova versão sem verificação de volume.
    Apenas registra a informação e prossegue.
    """
    chat_with_gpt(
        f"Ótimo, seu caminhão é {tamanho_caminhao}. Vamos prosseguir!",
        historico_conversa
    )
    return True  # Sempre retorna verdadeiro pois não temos como validar

def encaminhar_resultado_negociacao(status, resultado, preco_frete, destino_frete, numero_destino, historico_conversa):
    """
    Envia a mensagem final de encaminhamento do frete de acordo com o resultado da negociação.
    """
    if status in ["aceito", "aceito_com_acrescimo"]:
        preco_final = resultado
        chat_with_gpt(
            "Encaminhando contato e informações do frete.",
            historico_conversa,
            encaminhar_contato_local(preco_final, destino_frete, numero_destino)
        )
    elif status == "proposta":
        chat_with_gpt(
            "Encaminhando contato e informações do frete com sua proposta.",
            historico_conversa,
            encaminhar_contato_local(resultado, destino_frete, numero_destino)
        )
    else:
        chat_with_gpt(
            "Obrigado, até a próxima!",
            historico_conversa,
            tchau_caminhoneiro(False)
        )

def fluxo_negociacao(historico_conversa, frete_selecionado):
    """
    Fluxo atualizado sem verificação de volume.
    """
    if frete_selecionado is None:
        chat_with_gpt("Nenhum frete válido selecionado.", historico_conversa)
        return

    # Inicializa parâmetros
    numero_destino, preco_frete, origem_frete, destino_frete = inicializar_parametros_negociacao(frete_selecionado)
    
    # 1. Obter detalhes do caminhão (apenas coleta)
    tamanho_caminhao = obter_tamanho_caminhao(historico_conversa)
    
    # 2. Processar capacidade (apenas registra)
    if not processar_capacidade(tamanho_caminhao, historico_conversa):
        return
    
    # 3. Negociação de preço
    status, resultado = negociar_preco(preco_frete, historico_conversa)
    
    # 4. Finalização e encaminhamento
    if status in ["aceito", "aceito_com_acrescimo"]:
        mensagem_final = (
            f"✅ Confirmação do Frete ✅\n"
            f"• Origem: {origem_frete}\n"
            f"• Destino: {destino_frete}\n"
            f"• Valor: R$ {resultado:.2f}\n"
            f"• Tipo de Carga: Telhas\n\n"
            f"Por favor, confirme:\n"
            f"1. Nome completo\n"
            f"2. Número da CNH\n"
            f"3. Placa do veículo"
        )
    elif status == "proposta":
        mensagem_final = (
            f"📝 Proposta Recebida 📝\n"
            f"Sua oferta de R$ {resultado:.2f} foi registrada.\n"
            f"Estamos analisando e entraremos em contato em breve!"
        )
    else:
        mensagem_final = "Obrigado pelo contato! Volte sempre ✌️"
    
    chat_with_gpt(mensagem_final, historico_conversa)
    encaminhar_contato_local(resultado if status != "rejeicao" else preco_frete, destino_frete, numero_destino)

def main():
    # Carrega o histórico de conversa persistente
    historico_conversa = load_conversation_history()

    if len(sys.argv) < 2:
        print("Por favor, forneça um arquivo de áudio ou um prompt de texto.")
        return

    input_data = sys.argv[1]

    if os.path.isfile(input_data):
        file_extension = os.path.splitext(input_data)[1].lower()
        if file_extension == '.ogg':
            prompt = transcrever_audio(input_data, "Transcrevendo áudio...")
        else:
            print(f"Formato de arquivo '{file_extension}' não suportado para transcrição.")
            return
    else:
        prompt = input_data

    frete_selecionado = selecionar_frete(prompt, fretes_df)
    
    if frete_selecionado is not None:
        fluxo_negociacao(historico_conversa, frete_selecionado)
    else:
        chat_with_gpt("Desculpe, não encontrei fretes correspondentes. Poderia reformular sua solicitação?", historico_conversa)
    
    # Salva o histórico atualizado para as próximas interações
    save_conversation_history(historico_conversa)

if __name__ == "__main__":
    main()
