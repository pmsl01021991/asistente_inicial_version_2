from enum import Enum
import threading


class EstadoJarvis(Enum):
    ESPERANDO = "esperando"
    ESCUCHANDO = "escuchando"
    PENSANDO = "pensando"
    HABLANDO = "hablando"
    CONVERSANDO = "conversando"
    DURMIENDO = "durmiendo"
    PAUSADO = "pausado"          # NUEVO: Estado de pausa por interrupción


_lock = threading.Lock()
_estado_actual = EstadoJarvis.ESPERANDO

# NUEVOS FLAGS GLOBALES DE CONTROL
_interrumpido = False
_conversacion_pausada = False
_audio_detenido = False
_contexto_guardado = None


def obtener_estado():
    with _lock:
        return _estado_actual


def cambiar_estado(nuevo_estado):
    global _estado_actual
    with _lock:
        _estado_actual = nuevo_estado


def es(estado):
    with _lock:
        return _estado_actual == estado


# ========== NUEVAS FUNCIONES PARA CONTROL DE INTERRUPCIÓN ==========

def set_interrumpido(valor):
    global _interrumpido
    with _lock:
        _interrumpido = valor


def is_interrumpido():
    with _lock:
        return _interrumpido


def set_conversacion_pausada(valor):
    global _conversacion_pausada
    with _lock:
        _conversacion_pausada = valor


def is_conversacion_pausada():
    with _lock:
        return _conversacion_pausada


def set_audio_detenido(valor):
    global _audio_detenido
    with _lock:
        _audio_detenido = valor


def is_audio_detenido():
    with _lock:
        return _audio_detenido


def guardar_contexto(contexto):
    global _contexto_guardado
    with _lock:
        _contexto_guardado = contexto


def obtener_contexto_guardado():
    with _lock:
        return _contexto_guardado


def limpiar_contexto_guardado():
    global _contexto_guardado
    with _lock:
        _contexto_guardado = None


def reset_flags():
    """Reinicia todos los flags de interrupción"""
    global _interrumpido, _conversacion_pausada, _audio_detenido
    with _lock:
        _interrumpido = False
        _conversacion_pausada = False
        _audio_detenido = False