import os
import time
import threading


# ==========================
# ACCIONES DEL SISTEMA
# ==========================

def apagar_sistema():
    os.system("shutdown /s /t 0")


def reiniciar_sistema():
    os.system("shutdown /r /t 0")


def suspender_sistema():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")


# ==========================
# CUENTA REGRESIVA
# ==========================

def cuenta_regresiva(texto, accion, jarvis_ui):

    for i in range(10, 0, -1):
        jarvis_ui.actualizar_estado(f"{texto} en {i}...")
        time.sleep(1)

    accion()


# ==========================
# CONFIRMACIÓN POR VOZ
# ==========================

def confirmar_accion_por_voz(
        tipo,
        hablar,
        escuchar_comando,
        jarvis_ui
):

    mensajes = {
        "apagar": "apagar el sistema",
        "reiniciar": "reiniciar el sistema",
        "suspender": "suspender el sistema"
    }

    hablar(f"¿Está seguro de {mensajes[tipo]}? Diga sí o no.")

    inicio = time.time()
    tiempo_maximo = 8

    while time.time() - inicio < tiempo_maximo:

        respuesta = escuchar_comando(silencioso=True)

        if not respuesta:
            continue

        respuesta = respuesta.lower()

        # -----------------------
        # CONFIRMÓ
        # -----------------------
        if "sí" in respuesta or "si" in respuesta:

            hablar(f"{mensajes[tipo].capitalize()}, señor.")

            if tipo == "apagar":

                threading.Thread(
                    target=cuenta_regresiva,
                    args=("Apagando", apagar_sistema, jarvis_ui),
                    daemon=True
                ).start()

            elif tipo == "reiniciar":

                threading.Thread(
                    target=cuenta_regresiva,
                    args=("Reiniciando", reiniciar_sistema, jarvis_ui),
                    daemon=True
                ).start()

            elif tipo == "suspender":

                hablar("Suspendiendo el sistema.")
                suspender_sistema()

            return

        # -----------------------
        # CANCELÓ
        # -----------------------
        if "no" in respuesta:

            hablar("Acción cancelada.")
            return

    # -----------------------
    # NO RESPONDIÓ
    # -----------------------
    hablar("No recibí confirmación. Acción cancelada.")