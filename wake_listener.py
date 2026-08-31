import threading
import time
import speech_recognition as sr

import audio_manager
from voice_manager import voice_manager


class WakeListener:

    def __init__(self):

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 250
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.non_speaking_duration = 0.5

        self._activo = False
        self._thread = None
        self._callback = None

        self._microfono = sr.Microphone()

        with self._microfono as source:
            self.recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

    def iniciar(self, callback):

        self._callback = callback

        if self._activo:
            return

        self._activo = True

        self._thread = threading.Thread(
            target=self._escuchar,
            daemon=True
        )

        self._thread.start()

    def detener(self):

        self._activo = False

    def activo(self):

        return self._activo

    def _escuchar(self):

        while self._activo:

            if not audio_manager.esta_hablando():

                time.sleep(0.05)

                continue

            try:

                with self._microfono as source:

                    audio = self.recognizer.listen(
                        source,
                        timeout=0.8,
                        phrase_time_limit=2
                    )

                texto = voice_manager.reconocer(audio)

                if not texto:
                    continue

                texto = texto.lower().strip()

                print(f"[WakeListener] {texto}")

                if voice_manager.es_wake_word(texto):

                    print("[WakeListener] Interrumpiendo...")

                    audio_manager.detener()

                    while audio_manager.esta_hablando():
                        time.sleep(0.02)

                    if self._callback:

                        self._callback()

            except sr.WaitTimeoutError:

                continue

            except Exception as e:

                print("WakeListener:", e)

                time.sleep(0.1)

    def reiniciar(self):

        pass

    def esperando_interrupcion(self):

        return audio_manager.esta_hablando()

    def finalizar(self):

        self.detener()

        if self._thread:

            self._thread.join(timeout=2)