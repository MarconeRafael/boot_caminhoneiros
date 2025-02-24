import openai
import subprocess
import os
import sys

# Função para transcrever áudio OGG para WAV e depois transcrever o áudio para texto usando a API da OpenAI
def transcrever_audio(audio_ogg, message):
    """Converte um arquivo de áudio OGG para WAV e transcreve o áudio usando a API da OpenAI."""
    openai.api_key = "sua-chave-aqui"  # Substitua pela sua chave real
    
    audio_wav = audio_ogg.replace(".ogg", ".wav")
    
    if not os.path.exists(audio_ogg):
        message.reply(f"Arquivo {audio_ogg} não encontrado!")
        return
    
    # Converter OGG para WAV usando FFmpeg
    subprocess.run(["ffmpeg", "-i", audio_ogg, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", audio_wav], check=True)
    
    if not os.path.exists(audio_wav):
        message.reply(f"Erro na conversão! Arquivo {audio_wav} não foi gerado.")
        return
    
    # Transcrever o áudio WAV para texto utilizando a API da OpenAI (Whisper)
    with open(audio_wav, "rb") as audio_file:
        transcription = openai.Audio.transcribe("whisper-1", audio_file)
    
    transcricao_texto = transcription["text"]
    message.reply(f"Transcrição: {transcricao_texto}")
    return transcricao_texto

