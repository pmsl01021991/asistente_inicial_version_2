from vosk_local import reconocer_con_vosk

ACTIVADORES = (
    "jarvis",
    "oye jarvis",
    "hola jarvis",
    "jarvis estás ahí",
    "jarvis estas ahi",
)


class VoiceManager:

    def reconocer(self, audio):

        try:

            texto = reconocer_con_vosk(audio)

            if not texto:
                return ""

            return texto.lower().strip()

        except Exception:
            return ""

    def es_wake_word(self, texto):

        if not texto:
            return False

        texto = texto.lower().strip()

        for activador in ACTIVADORES:

            if activador == texto:
                return True

            if texto.startswith(activador + " "):
                return True

        return False


voice_manager = VoiceManager()