from vosk import Model, KaldiRecognizer
import json
import os
import sys

def recurso(ruta):
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base, ruta)

RUTA_MODELO = recurso("vosk-model-small-es-0.42")

modelo_vosk = Model(RUTA_MODELO)

def reconocer_con_vosk(audio):
    datos = audio.get_raw_data(convert_rate=16000, convert_width=2)

    rec = KaldiRecognizer(modelo_vosk, 16000)

    if rec.AcceptWaveform(datos):
        resultado = json.loads(rec.Result())
    else:
        resultado = json.loads(rec.FinalResult())

    return resultado.get("text", "").strip()