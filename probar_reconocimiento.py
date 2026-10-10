
import reconocimiento_facial as facial


def hablar(texto):
    print("JARVIS:", texto)


facial.reconocer_rostro(hablar)
