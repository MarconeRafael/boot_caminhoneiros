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
    base_system_message = "Você é um atendente simpático, que conversa de maneira clara e amigável com caminhoneiros afim de contratar o serviço de fretes deles."
    full_system_message = (base_system_message + " " + system_message) if system_message else base_system_message

    # Adiciona a mensagem do usuário ao histórico
    conversation_history.append({"role": "user", "content": prompt})

    # Realiza a chamada à API do GPT
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": full_system_message}] + conversation_history
    )

    # Extrai a resposta do modelo
    reply = response.choices[0].message['content']

    # Atualiza o histórico com a resposta do GPT
    conversation_history.append({"role": "assistant", "content": reply})

    return reply

# Caso você precise implementar uma versão local da função de encaminhamento, segue um exemplo:
def encaminhar_contato_local(preco_frete, destino_frete, quantidade_telha, tipo_telhas, numero_destino):
    """
    Envia as informações do frete via WhatsApp para o número de destino.
    Neste exemplo, a mensagem é exibida via print.
    """
    # Converte preco_frete para float, caso esteja como string
    try:
        preco_frete_num = float(preco_frete)
    except ValueError:
        preco_frete_num = 0.0

    mensagem = (
        f"Detalhes do Frete:\n"
        f"📍 Destino: {destino_frete}\n"
        f"📦 Quantidade de Telhas: {quantidade_telha}\n"
        f"🏗️ Tipo de Telhas: {tipo_telhas}\n"
        f"💰 Preço do Frete: R$ {preco_frete_num:.2f}"
    )
    
    # Simula o envio da mensagem (substitua por sua implementação real)
    print("Enviando mensagem para", numero_destino)
    print(mensagem)
    
    return mensagem


def fluxo(historico_conversa):
    """
    Executa o fluxo de conversação com o caminhoneiro a partir do interesse em um frete.
    
    Fluxo:
      1. Receber interesse em um frete específico.
      2. Perguntar o tamanho do caminhão.
      3. Verificar se o frete cabe no caminhão.
         - Se couber:
             a. Oferecer o preço do frete.
                 - Se aceitar: encaminhar o contato e as informações do frete.
                 - Se comentar sobre o valor: oferecer acréscimo de 10%.
                     * Se aceitar: encaminhar contato.
                     * Se não aceitar: perguntar qual a proposta e encaminhar.
                 - Se não aceitar: despedir-se.
         - Se não couber: despedir-se do caminhoneiro.
    """
    if fretes_df is None or fretes_df.empty:
        print("Erro ao carregar os fretes. Verifique o arquivo ou os dados.")
        return

    # Seleciona o primeiro frete disponível para este exemplo
    frete_selecionado = fretes_df.iloc[0]
    numero_destino = numero_destino1  # Número para encaminhar contato

    # Dados do frete selecionado
    volume_frete = frete_selecionado['Carga']
    preco_frete = frete_selecionado['Preço']
    destino_frete = frete_selecionado['Destino']

    # Dados extras (estes valores podem ser dinâmicos ou oriundos de outra fonte)
    quantidade_telha = 100      # Exemplo de quantidade
    tipo_telhas = "Cerâmicas"   # Exemplo de tipo

    # 1. Perguntar o tamanho do caminhão
    system_msg = perguntar_tamanho_caminhao()
    system_msg += "Respostas:" + " " + str(volume_frete) + " " + str(preco_frete) + " " + str(destino_frete)

    tamanho_caminhao = chat_with_gpt("Qual o tamanho do seu caminhão?", historico_conversa, system_msg)

    # 2. Verificar se o frete cabe no caminhão
    caber = verificar_capacidade(volume_frete, tamanho_caminhao)
    
    if caber:
        # 3. Oferecer o preço do frete
        system_msg = oferecer_preco(preco_frete)
        resposta_preco = chat_with_gpt(f"Ofereço o frete por R$ {preco_frete}. Você aceita?", historico_conversa, system_msg)

        if "aceito" in resposta_preco.lower():
            # Caminhoneiro aceitou o preço
            system_msg = encaminhar_contato_local(preco_frete, destino_frete, quantidade_telha, tipo_telhas, numero_destino)
            chat_with_gpt("Encaminhando contato e informações do frete.", historico_conversa, system_msg)
        elif "valor" in resposta_preco.lower():
            # Caminhoneiro comentou sobre o preço
            novo_preco = preco_frete * 1.10  # Acréscimo de 10%
            system_msg = oferecer_acrescimo(novo_preco)
            resposta_acrescimo = chat_with_gpt(f"Posso ajustar para R$ {novo_preco}? Você aceita?", historico_conversa, system_msg)
            if "aceito" in resposta_acrescimo.lower():
                system_msg = encaminhar_contato_local(novo_preco, destino_frete, quantidade_telha, tipo_telhas, numero_destino)
                chat_with_gpt("Encaminhando contato e informações com o novo preço.", historico_conversa, system_msg)
            else:
                system_msg = perguntar_proposta()
                proposta = chat_with_gpt("Qual a sua proposta?", historico_conversa, system_msg)
                system_msg = encaminhar_contato_local(proposta, destino_frete, quantidade_telha, tipo_telhas, numero_destino)
                chat_with_gpt("Encaminhando contato e informações do frete com sua proposta.", historico_conversa, system_msg)
        else:
            # Caminhoneiro não aceitou o preço inicial
            system_msg = tchau_caminhoneiro(False)
            chat_with_gpt("Obrigado, até a próxima!", historico_conversa, system_msg)
    else:
        # Caso o frete não caiba no caminhão, realiza despedida
        system_msg = tchau_caminhoneiro(False)
        chat_with_gpt("Infelizmente, seu caminhão não comporta este frete. Obrigado!", historico_conversa, system_msg)

def main():
    """
    Função principal que processa a entrada (áudio ou texto), executa o fluxo e interage com o GPT.
    """
    # Inicializa o histórico de conversa
    historico_conversa = []

    # Executa o fluxo do frete antes de tratar a entrada do usuário
    fluxo(historico_conversa)

    # Verifica se o usuário forneceu uma entrada (áudio ou texto) via argumentos
    if len(sys.argv) < 2:
        print("Por favor, forneça um arquivo de áudio ou um prompt de texto.")
        sys.exit(1)

    input_data = sys.argv[1]

    # Se a entrada for um arquivo, verifica a extensão
    if os.path.isfile(input_data):
        file_extension = os.path.splitext(input_data)[1].lower()
        if file_extension == '.ogg':
            prompt = transcrever_audio(input_data, "Transcrevendo áudio...")
        else:
            print(f"Formato de arquivo '{file_extension}' não suportado para transcrição.")
            sys.exit(1)
    else:
        prompt = input_data

    # Envia o prompt final para o GPT e exibe a resposta
    resposta_final = chat_with_gpt(prompt, historico_conversa, "Processando sua solicitação.")
    print(resposta_final)

if __name__ == "__main__":
    main()
