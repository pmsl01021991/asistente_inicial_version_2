import requests
import json

from memoria import (
    memoria,
    historial_conversacion,
    analizar_y_guardar_info,
    guardar_memoria
)

MODELO = "llama3.2:3b"

class OllamaManager:

    def __init__(self):

        self.system_prompt = {
            "role": "system",
            "content": (
                "Eres Jarvis, el asistente personal del usuario. "
                "Habla de forma natural, educada e inteligente. "
                "Nunca digas que eres un modelo de IA. "
                "Mantén el contexto de la conversación. "
                "No inventes información cuando no la conozcas. "
                "Responde de forma natural y con suficiente detalle para explicar bien la respuesta, normalmente entre 2 y 5 frases. Si la pregunta es sencilla, responde brevemente. Si requiere explicación, puedes extenderte."
            )
        }

    def preguntar(self, texto):

        # Analizar si el usuario enseñó información nueva
        analizar_y_guardar_info(texto)

        # Construir contexto con la memoria
        contexto_memoria = (
            "Toda la información a continuación pertenece al usuario que está hablando. "
            "El usuario ha dado permiso explícito para recordar y utilizar estos datos personales "
            "para responder correctamente.\n"
            + json.dumps(memoria, ensure_ascii=False)
        )

        # Agregar pregunta al historial persistente
        historial_conversacion.append({
            "role": "user",
            "content": contexto_memoria + "\n\n" + texto
        })

        # Limitar historial
        mensajes = historial_conversacion[-8:]

        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": MODELO,
                "messages": [self.system_prompt] + mensajes,
                
                "stream": False,
                "keep_alive": "20m",
                "options": {
                    "temperature": 0.25,
                    "top_p": 0.75,
                    "top_k": 15,
                    "repeat_penalty": 1.05,
                    "num_predict": 100,
                    "num_ctx": 1024
                }
            },
            timeout=60
        )

        response.raise_for_status()

        respuesta = response.json()["message"]["content"].strip()
        print("Respuesta de Ollama:", respuesta)
        # Guardar respuesta
        historial_conversacion.append({
            "role": "assistant",
            "content": respuesta
        })

        return respuesta
    
    def continuar_conversacion(self, instruccion):

        mensajes = self.historial.copy()

        mensajes.append({
            "role": "system",
            "content": instruccion
        })

        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": MODELO,
                "messages": mensajes,
                "stream": False,
                "keep_alive": "20m",
                "options": {
                    "temperature": 0.25,
                    "top_p": 0.9,
                    "top_k": 15,
                    "repeat_penalty": 1.1,
                    "num_predict": 120,
                    "num_ctx": 2048
                }
            },
            timeout=60
        )

        response.raise_for_status()

        respuesta = response.json()["message"]["content"].strip()

        self.historial.append({
            "role": "assistant",
            "content": respuesta
        })

        return respuesta

    def limpiar_memoria(self):

        self.historial = [self.historial[0]]

    def agregar_contexto(self, texto):

        self.historial.append({
            "role": "system",
            "content": texto
        })


ollama = OllamaManager()