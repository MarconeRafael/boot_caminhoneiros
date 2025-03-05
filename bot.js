const { Client } = require('whatsapp-web.js');
const axios = require('axios');

// Inicializando o cliente do WhatsApp
const client = new Client();

client.on('qr', qr => {
    console.log('QR Code:', qr);
});

client.on('ready', () => {
    console.log('WhatsApp Bot está pronto!');
});

client.on('message', async (msg) => {
    if (msg.body.toLowerCase().includes('frete')) {
        // Passo 1: Receber mensagem de interesse no frete
        msg.reply('Você está interessado em um frete. Qual o tamanho do caminhão?');
    } else if (msg.body.toLowerCase().includes('pequeno') || msg.body.toLowerCase().includes('médio') || msg.body.toLowerCase().includes('grande')) {
        // Passo 2: Receber o tamanho do caminhão
        const tamanho = msg.body;
        msg.reply(`O caminhão é de tamanho: ${tamanho}. Agora vamos encaminhar as informações.`);

        // Passo 3: Encaminhar as informações para o número de destino
        const numeroDestino = '558498888888@c.us';  // Número do contato de destino
        const infoFrete = `Frete: ${tamanho} - Caminhoneiro: ${msg.from}`;
        
        try {
            await client.sendMessage(numeroDestino, infoFrete);
            msg.reply('As informações foram encaminhadas para o caminhoneiro.');
        } catch (error) {
            console.error('Erro ao encaminhar informações:', error);
            msg.reply('Houve um erro ao encaminhar as informações.');
        }
    }
});

// Iniciar o cliente
client.initialize();
