def encaminhar_contato(preco_frete, destino_frete, quantidade_telha, tipo_telhas, numero_destino, message):
    """
    Envia as informações do frete via WhatsApp para o número de destino.
    """
    # Monta a mensagem com os detalhes do frete
    mensagem = (
        f"Detalhes do Frete:\n"
        f"📍 Destino: {destino_frete}\n"
        f"📦 Quantidade de Telhas: {quantidade_telha}\n"
        f"🏗️ Tipo de Telhas: {tipo_telhas}\n"
        f"💰 Preço do Frete: R$ {preco_frete:.2f}"
    )
    
    # Envia a mensagem de resposta ao usuário
    message.reply(mensagem)
    
    return mensagem


