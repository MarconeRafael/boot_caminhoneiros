def verificar_capacidade(volume_frete, volume_caminhao, message):
    """
    Verifica se o volume do frete cabe no volume disponível do caminhão e envia uma resposta.
    """
    if isinstance(volume_frete, (int, float)) and isinstance(volume_caminhao, (int, float)):
        if volume_frete <= volume_caminhao:
            resposta = "O volume do frete cabe no caminhão."
        else:
            resposta = "O volume do frete não cabe no caminhão."
    else:
        resposta = "Erro: os volumes fornecidos não são numéricos."
    
    # Envia a resposta ao usuário usando message.reply()
    message.reply(resposta)
    
    return resposta

