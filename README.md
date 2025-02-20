
# Caminhoneiro Chatbot para WhatsApp

Este projeto implementa um chatbot de caminhoneiro integrado ao WhatsApp usando a API da OpenAI. O chatbot simula um caminhoneiro experiente que negocia viagens e interage de forma descontraída.

## Funcionalidades
- Mantém o contexto da conversa
- Responde de forma bem-humorada e típica de caminhoneiros
- Negocia valores para viagens específicas:
  - Caso o usuário mencione uma viagem não listada, informa as opções disponíveis
  - Pergunta o tamanho do caminhão e verifica se o frete de interesse cabe
  - Se o frete couber, oferece o preço
  - Se o caminhoneiro aceitar, envia o contato e as informações do frete
  - Se o caminhoneiro questionar sobre o preço, oferece um acréscimo de 10% e verifica se ele aceita
  - Se o caminhoneiro recusar, mostra a lista de fretes novamente e repete o processo
  - Caso o caminhoneiro não se interesse por outros fretes, o chatbot se despede
- Quando um caminhoneiro fechar um acordo, um número de um atendente humano receberá o número do caminhoneiro e o frete que ele fechou
- Suporte para áudios: o chatbot agora aceita mensagens de áudio e realiza a transcrição para texto

## Requisitos
- Python 3.8+
- OpenAI API Key
- Node.js 14.x ou superior
- Ambiente virtual configurado (para o Python)
- Dependências do Node.js

## Instalação

### 1. Clone o repositório:
```bash
git clone https://github.com/seu-repositorio/caminhoneiro-bot.git
cd caminhoneiro-bot
```

### 2. Crie e ative um ambiente virtual (para o Python):
```bash
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scriptsctivate
```

### 3. Instale as dependências Python:
```bash
pip install -r requirements.txt
```

### 4. Instale as dependências Node.js:
Primeiro, instale as dependências necessárias para o funcionamento do WhatsApp Bot. No diretório do projeto, execute:
```bash
npm install qrcode-terminal whatsapp-web.js express axios
```

## Configuração

Crie um arquivo `keys.py` com a sua chave da OpenAI:
```python
chave_openai = "SUA_CHAVE_AQUI"
```

## Uso

### 1. Execute o chatbot Python:
Primeiro, inicie o chatbot para interagir com o terminal:
```bash
python caminhoneiro.py
```

### 2. Execute o WhatsApp Bot com Node.js:
Em outro terminal, execute o bot de WhatsApp:
```bash
node whatsapp_bot.js

```

Agora, o chatbot estará integrado com o WhatsApp e poderá negociar viagens com os usuários.

## Integração com WhatsApp
Este projeto usa o **whatsapp-web.js**, uma biblioteca Node.js para interagir com o WhatsApp Web. Isso permite enviar e receber mensagens diretamente do WhatsApp.

### Dependências do Node.js:
- `qrcode-terminal`: Para gerar o QR Code de autenticação do WhatsApp Web.
- `whatsapp-web.js`: Para gerenciar a comunicação com o WhatsApp.
- `express`: Para servidor web (caso queira expandir a funcionalidade).
- `axios`: Para realizar chamadas HTTP, se necessário.

Caso o QR Code não apareça, execute:
```bash
rm -rf .wwebjs_auth .wwebjs_cache
```

## Contribuição
Sinta-se à vontade para contribuir! Envie um pull request ou abra uma issue caso encontre problemas ou tenha sugestões.

## Licença
Este projeto está sob a licença Apache 2.0.
