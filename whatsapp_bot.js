const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { spawn } = require('child_process');
const fs = require('fs');

// Caminho do arquivo JSON
const caminhoJson = 'mensagens.json';

// Função para salvar mensagens no JSON
const salvarMensagem = (numero_remetente, mensagem) => {
    let mensagens = [];

    // Lê o arquivo JSON se já existir
    if (fs.existsSync(caminhoJson)) {
        const dados = fs.readFileSync(caminhoJson);
        mensagens = JSON.parse(dados);
    }

    // Adiciona a nova mensagem
    mensagens.push({ numero_remetente, mensagem, timestamp: new Date().toISOString() });

    // Salva no arquivo
    fs.writeFileSync(caminhoJson, JSON.stringify(mensagens, null, 4));
};

// Inicializa o cliente do WhatsApp
const client = new Client({
    authStrategy: new LocalAuth()
});

// Gerar e exibir o QR Code para autenticação
client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
    console.log("QR Code gerado, escaneie com seu WhatsApp.");
});

// Quando o cliente estiver pronto
client.on('ready', () => {
    console.log('WhatsApp Bot está pronto!');
});

// Quando uma nova mensagem chegar
client.on('message', async (msg) => {
    try {
        console.log(`Mensagem recebida de ${msg.from}:`, msg.body);

        // Obtém o número do remetente
        const numero_remetente = msg.from;

        // Salva a mensagem no JSON
        salvarMensagem(numero_remetente, msg.body);

        // Chama o script Python passando o número do remetente
        const pythonProcess = spawn(process.platform === 'win32' ? 'python' : 'python3', ['teste.py', msg.body, numero_remetente]);

        // Captura a resposta do stdout do Python
        pythonProcess.stdout.on('data', (data) => {
            const resposta = data.toString().trim();
            console.log("Resposta do Python:", resposta);
            msg.reply(resposta);
        });

        // Captura erros do processo Python
        pythonProcess.stderr.on('data', (data) => {
            console.error(`Erro no Python: ${data}`);
        });

        // Captura se o processo for encerrado inesperadamente
        pythonProcess.on('close', (code) => {
            console.log(`Processo Python encerrado com código ${code}`);
        });

    } catch (error) {
        console.error("Erro ao processar mensagem:", error);
    }
});

// Inicializa o cliente do WhatsApp
client.initialize();
