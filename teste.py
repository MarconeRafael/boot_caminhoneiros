from perguntar_tamanho_caminhao import perguntar_tamanho_caminhao
from keys import chave_openai, numero_destino1
from fretes import carregar_fretes
from oferecer_preco import oferecer_preco

# Carregar os dados de fretes
fretes_df, fretes_dict, lista_fretes_str = carregar_fretes(caminho_arquivo="data/xls/fretes.xlsx")
numero_destino = numero_destino1

# Função principal de encaminhamento
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
    
    # Envia mensagem para o número de destino (simulação)
    print(f"Enviando mensagem para {numero_destino}: {mensagem}")

# Loop para enviar mensagens para todos os fretes
for _, row in fretes_df.iterrows():
    destino_frete = row['Destino']
    preco_frete = row['Preço']  # Preço do frete para cada destino
    mensagem1 = perguntar_tamanho_caminhao()  # Pergunta o tamanho do caminhão
    mensagem2 = oferecer_preco(preco_frete)  # Oferece o preço do frete

    # Envia mensagem final de frete
    encaminhar_contato_local(preco_frete, destino_frete, numero_destino)
