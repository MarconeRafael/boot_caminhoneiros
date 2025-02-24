def verificar_capacidade(volume_frete, volume_caminhao):
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
    

    
    return resposta

