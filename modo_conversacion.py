import threading
import time

import audio_manager
from ollama_manager import ollama


class ConversationManager:

    def __init__(self):

        self._activo = False
        self._modo_activo = False

        self._thread = None

        self._callback_hablar = None

        self._ultima_interaccion = time.time()

        self._tiempo_inicial = 5
        self._tiempo_entre_frases = 5
        self._pausado = False

    def iniciar(self, callback_hablar):

        self._callback_hablar = callback_hablar

        if self._activo:
            return

        self._activo = True

        self._thread = threading.Thread(
            target=self._loop,
            daemon=True
        )

        self._thread.start()

    def detener(self):

        self._activo = False

    def activar(self):

        self._modo_activo = True

        self._ultima_interaccion = time.time()

    def desactivar(self):

        self._modo_activo = False

    def activo(self):

        return self._modo_activo

    def actualizar_interaccion(self):

        self._ultima_interaccion = time.time()

    def _esperar_fin_audio(self):

        while audio_manager.esta_hablando():

            time.sleep(0.1)
            
    def pausar(self):

        self._pausado = True


    def reanudar(self):

        self._pausado = False
        self._ultima_interaccion = time.time()

    def _loop(self):

        while self._activo:
            
            if self._pausado:

                time.sleep(0.2)

                continue

            if not self._modo_activo:

                time.sleep(0.5)

                continue

            segundos = time.time() - self._ultima_interaccion

            if segundos < self._tiempo_inicial:

                time.sleep(0.5)

                continue

            break

        while self._activo:
        
            if not self._modo_activo:

                time.sleep(0.5)

                continue
            
            if audio_manager.esta_hablando():

                time.sleep(0.2)

                continue

            try:

                prompt = self.generar_prompt()

                respuesta = ollama.continuar_conversacion(prompt)

                if respuesta:

                    texto = respuesta.strip()

                    if texto.lower().startswith(("hola", "buenas", "¿cómo puedo", "como puedo")):
                        continue

                    if self._callback_hablar:
                        self._callback_hablar(
                            texto,
                            mostrar=True
                        )

                self._esperar_fin_audio()

            except Exception as e:

                print("ConversationManager:", e)

            tiempo = 0

            while tiempo < self._tiempo_entre_frases:

                if not self._modo_activo:
                    break

                time.sleep(1)

                tiempo += 1

    def generar_prompt(self):

        return (
            "Eres Jarvis, el asistente personal del usuario. "
            "Ya estás en medio de una conversación. "
            "NO inicies una conversación nueva. "
            "NO saludes. "
            "NO digas 'Hola'. "
            "NO digas '¿En qué puedo ayudarte?'. "
            "NO preguntes si necesita algo. "
            "Continúa naturalmente desde la última idea del historial. "
            "Si terminaste un tema, enlaza con otro relacionado de forma fluida. "
            "Habla como una persona inteligente y segura. "
            "No repitas frases anteriores. "
            "No digas que eres una IA. "
            "Responde únicamente con la continuación de la conversación."
        )
        
    def cambiar_tiempo_entre_frases(self, segundos):

        self._tiempo_entre_frases = segundos


    def cambiar_tiempo_inicial(self, segundos):

        self._tiempo_inicial = segundos


    def reiniciar_temporizador(self):

        self._ultima_interaccion = time.time()


    def esta_conversando(self):

        return self._modo_activo