def despedir_caminhoneiro(message):
    """
    Envia uma mensagem de despedida após a recusa do caminhoneiro.
    """
    # Mensagem de despedida do sistema após a recusa do caminhoneiro
    mensagem = (
        "Entendemos sua decisão. Agradecemos pela sua disponibilidade e esperamos poder contar com você em outra oportunidade. Até logo!"
    )
    
    # Caso haja necessidade de registrar a recusa ou a situação no sistema
    # registrar_evento("Caminhoneiro recusou o frete e se despediu.")
    
    # Encerramento de qualquer outro processo, se necessário
    # exemplo: limpar_dados_do_caminhoneiro()

    # Envia a mensagem de despedida ao usuário
    message.reply(mensagem)
    
    return mensagem


