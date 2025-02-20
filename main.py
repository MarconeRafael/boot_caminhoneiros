from receber_mensagem import receber_mensagem
from perguntar_tamanho_caminhao import perguntar_tamanho_caminhao
from verificar_capacidade import verificar_capacidade
from oferecer_preco import oferecer_preco
from encaminhar_contato import encaminhar_contato
from oferecer_acrescimo import oferecer_acrescimo
from perguntar_proposta import perguntar_proposta
from despedir_caminhoneiro import despedir_caminhoneiro
from fretes import carregar_fretes
from keys import numero_destino1, chave_openai
import openai

# Definindo uma classe para simular o objeto message
class DummyMessage:
    def reply(self, mensagem):
        print("Reply:", mensagem)

# Carregar os fretes
fretes_df, fretes_dict, lista_fretes_str = carregar_fretes()

# Função para utilizar o GPT para determinar a intenção da resposta
def analisar_resposta_com_gpt(mensagem):
    try:
        openai.api_key = chave_openai  # A chave da API GPT, que você deve ter em seu arquivo keys.py
        
        resposta = openai.Completion.create(
            model="gpt-3.5-turbo",  # Ou o modelo mais barato disponível
            prompt=f"Analisando a mensagem: '{mensagem}'. A resposta é positiva ou negativa? A resposta é uma confirmação de 'sim', uma proposta de negociação ou uma recusa?",
            max_tokens=50
        )
        
        retorno = resposta.choices[0].text.strip().lower()
        
        if "sim" in retorno:
            return "sim"
        elif "negociar" in retorno:
            return "negociar"
        else:
            return "não"
    
    except Exception as e:
        print(f"Erro ao analisar a resposta com GPT: {e}")
        return "não"

def main():
    # Simulando o objeto message para testes
    message = DummyMessage()

    # Verificar se os fretes foram carregados corretamente
    if fretes_df is None:
        print("Erro ao carregar os fretes. O DataFrame está vazio ou não foi carregado corretamente.")
        return

    # Iterar sobre todos os fretes
    for _, frete_selecionado in fretes_df.iterrows():
        numero_destino = numero_destino1  # Substitua pelo número real
        
        # Extraindo os dados de cada frete
        volume_frete = frete_selecionado['Carga']  # Coluna 'Carga'
        preco_frete = frete_selecionado['Preço']   # Coluna 'Preço'
        destino_frete = frete_selecionado['Destino'] # Coluna 'Destino'
        
        # Suponha que a quantidade de telhas e o tipo de telha sejam valores fixos ou provenientes de outra fonte
        quantidade_telha = 100   # Ou obtenha de outra forma
        tipo_telhas = "Cerâmica" # Ou obtenha de outra forma
        
        # Perguntar se o caminhoneiro está interessado
        interesse = receber_mensagem(message)
        if not interesse:
            despedir_caminhoneiro(message)
            return
        
        volume_caminhao = perguntar_tamanho_caminhao(message)
        
        if verificar_capacidade(volume_frete, volume_caminhao, message):
            resposta = oferecer_preco(preco_frete, message)
            
            resposta_analizada = analisar_resposta_com_gpt(resposta)
            
            if resposta_analizada == "sim":
                # Se o caminhoneiro aceitar, encaminha os detalhes
                encaminhar_contato(preco_frete, destino_frete, quantidade_telha, tipo_telhas, numero_destino, message)
            elif resposta_analizada == "negociar":
                # Caso haja negociação, oferece um acréscimo
                resposta_negociacao = oferecer_acrescimo(preco_frete, message)
                
                resposta_negociacao_analizada = analisar_resposta_com_gpt(resposta_negociacao)
                
                if resposta_negociacao_analizada == "sim":
                    # Se aceitar o acréscimo, encaminha com o novo preço
                    encaminhar_contato(preco_frete * 1.1, destino_frete, quantidade_telha, tipo_telhas, numero_destino, message)
                else:
                    # Caso a negociação não seja aceita, pergunta uma proposta
                    proposta = perguntar_proposta(message)
                    encaminhar_contato(proposta, destino_frete, quantidade_telha, tipo_telhas, numero_destino, message)
            else:
                # Caso a resposta seja negativa, despede o caminhoneiro
                despedir_caminhoneiro(message)
        else:
            # Caso o caminhão não tenha capacidade suficiente, despede o caminhoneiro
            despedir_caminhoneiro(message)

if __name__ == "__main__":
    main()
