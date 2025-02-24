// whatsapp_bot.js

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { spawn } = require('child_process');

// Inicializa o cliente do WhatsApp
const client = new Client({
    authStrategy: new LocalAuth() // Mantém a sessão salva localmente
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
client.on('message', msg => {
    console.log("Mensagem recebida:", msg.body);

    // Chama o script Python (main.py) passando a mensagem como argumento
    const pythonProcess = spawn('python', ['main.py', msg.body]);

    // Captura a resposta do stdout do Python
    pythonProcess.stdout.on('data', (data) => {
        const resposta = data.toString().trim();
        console.log("Resposta do Python:", resposta);

        // Envia a resposta de volta para o remetente no WhatsApp
        msg.reply(resposta);
    });

    // Captura erros (caso ocorram)
    pythonProcess.stderr.on('data', (data) => {
        console.error(`Erro no Python: ${data}`);
    });
});

// Inicializa o cliente do WhatsApp
client.initialize();
