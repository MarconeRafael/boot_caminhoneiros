class DummyMessage:
    def reply(self, mensagem):
        print(mensagem)

def tchau_caminhoneiro(mensagem_enviada=False):
    """
    Retorna uma mensagem de despedida após a recusa do caminhoneiro.
    Impede o envio repetido da mesma mensagem.
    """
    if mensagem_enviada:
        return "Mensagem já enviada."

    return (
        "🚛 Entendemos sua decisão. Agradecemos pela sua disponibilidade e esperamos poder contar com você em outra oportunidade. Até logo!"
    )
