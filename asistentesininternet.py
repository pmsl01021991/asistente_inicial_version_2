import subprocess
import winsound
import os
import requests
import uuid
from faster_whisper import WhisperModel
import sounddevice as sd
from scipy.io.wavfile import write

MODELO = "smollm2:360m"

# Whisper local
whisper = WhisperModel("base", device="cpu", compute_type="int8")

historial = [
    {
        "role": "system",
        "content": "Eres Jarvis, asistente personal del usuario. "
                        "Responde de forma coherente, clara y natural. "
                        "No inventes información. "
                        "Mantén el contexto de la conversación. "
                        "No digas 'como modelo de IA'. "
                        "No rechaces tareas normales como crear saludos, mensajes para TikTok, WhatsApp o redes sociales. "
                        "Si el usuario dice que te está grabando, continúa normal y responde con naturalidad."
    }
]

PIPER_EXE = r"E:\piper_windows_amd64\piper\piper.exe"
PIPER_MODEL = r"E:\piper_windows_amd64\piper\voices\es_ES-carlfm-x_low.onnx"

def grabar_audio(duracion=5, archivo="entrada.wav"):
    print("\n🎤 Escuchando...")
    fs = 16000
    audio = sd.rec(int(duracion * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    write(archivo, fs, audio)
    return archivo

def transcribir_audio(archivo):
    segments, info = whisper.transcribe(
        archivo,
        language="es",
        beam_size=1
    )

    texto = ""
    for segment in segments:
        texto += segment.text

    return texto.strip()

def hablar(texto, mostrar=False):
    if mostrar:
        print("Jarvis:", texto)

    archivo_salida = f"voz_{uuid.uuid4()}.wav"

    comando = [
        PIPER_EXE,
        "--model", PIPER_MODEL,
        "--output_file", archivo_salida
    ]

    subprocess.run(
        comando,
        input=texto,
        text=True,
        encoding="utf-8",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    winsound.PlaySound(archivo_salida, winsound.SND_FILENAME)

    if os.path.exists(archivo_salida):
        os.remove(archivo_salida)

def preguntar_ollama(texto):
    global historial

    historial.append({
        "role": "user",
        "content": texto
    })

    if len(historial) > 7:
        historial = [historial[0]] + historial[-6:]

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": MODELO,
            "messages": historial,
            "stream": False,
            "keep_alive": "10m",
            "options": {
                "num_predict": 50,
                "num_ctx": 1024,
                "temperature": 0.6,
                "repeat_penalty": 1.2
            }
        },
        timeout=60
    )

    data = response.json()
    respuesta = data["message"]["content"].strip()

    historial.append({
        "role": "assistant",
        "content": respuesta
    })

    return respuesta

hablar("Jarvis iniciado.")

while True:
    try:
        archivo_audio = grabar_audio(duracion=5)
        texto = transcribir_audio(archivo_audio)

        if os.path.exists(archivo_audio):
            os.remove(archivo_audio)

        if not texto:
            print("No entendí lo que dijiste.")
            continue

        print("Tú:", texto)

        if "salir" in texto.lower() or "cerrar" in texto.lower():
            hablar("Hasta luego bro.")
            break

        respuesta = preguntar_ollama(texto)
        hablar(respuesta, mostrar=False)

    except Exception as e:
        print("Error:", e)