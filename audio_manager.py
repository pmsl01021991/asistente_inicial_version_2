import pygame
import threading
import time

pygame.mixer.init()

_lock = threading.RLock()

_hilo_actual = None
_hablando = False
_detener = False
_pausado = False


def esta_hablando():
    return _hablando


def esta_pausado():
    return _pausado


def detener():
    global _detener

    _detener = True

    try:
        pygame.mixer.music.stop()
    except:
        pass


def pausar():
    global _pausado

    if _hablando:
        try:
            pygame.mixer.music.pause()
            _pausado = True
        except:
            pass


def reanudar():
    global _pausado

    if _pausado:
        try:
            pygame.mixer.music.unpause()
            _pausado = False
        except:
            pass


def reproducir(ruta_audio):

    global _hablando
    global _detener
    global _pausado

    with _lock:

        _detener = False
        _pausado = False
        _hablando = True

        try:

            pygame.mixer.music.load(ruta_audio)
            pygame.mixer.music.play()

            while True:

                if _detener:
                    pygame.mixer.music.stop()
                    break

                if _pausado:
                    time.sleep(0.05)
                    continue

                if not pygame.mixer.music.get_busy():
                    break

                time.sleep(0.02)

        finally:

            _hablando = False
            _detener = False
            _pausado = False


def reproducir_async(ruta_audio):

    global _hilo_actual

    detener()

    if _hilo_actual and _hilo_actual.is_alive():
        _hilo_actual.join(timeout=1)

    _hilo_actual = threading.Thread(
        target=reproducir,
        args=(ruta_audio,),
        daemon=True
    )

    _hilo_actual.start()


def esperar_fin():

    if _hilo_actual:
        _hilo_actual.join()