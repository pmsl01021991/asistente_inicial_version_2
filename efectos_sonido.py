import os
import time
from playsound import playsound


def reproducir_aplausos(hablar, jarvis_ui, estado):

    archivo = estado["recurso"]("aplausos.mp3")

    if not os.path.exists(archivo):
        hablar("No encontré el archivo de aplausos, señor.")
        return

    try:
        estado["jarvis_hablando"] = True
        estado["escuchando"] = False

        jarvis_ui.actualizar_estado("👏 Aplausos")

        playsound(archivo)

        estado["ultimo_audio"] = time.time()
        time.sleep(0.3)

    except Exception as e:
        print("Error reproduciendo aplausos:", e)

    finally:
        estado["jarvis_hablando"] = False

        if not estado["microfono_bloqueado"]:
            estado["escuchando"] = True
            jarvis_ui.cambiar_color_texto("Esperando")
            jarvis_ui.actualizar_estado("Esperando comando...")
        else:
            estado["escuchando"] = False
            jarvis_ui.cambiar_color_texto("microfono_desactivado")
            jarvis_ui.actualizar_estado("🎙️ Micrófono desactivado")



def reproducir_risas(hablar, jarvis_ui, estado):

    archivo = estado["recurso"]("risas.mp3")

    if not os.path.exists(archivo):
        hablar("No encontré el archivo de risas, señor.")
        return

    try:
        estado["jarvis_hablando"] = True
        estado["escuchando"] = False

        jarvis_ui.actualizar_estado("😂 Riendo")

        playsound(archivo)

        estado["ultimo_audio"] = time.time()
        time.sleep(0.3)

    except Exception as e:
        print("Error reproduciendo risas:", e)

    finally:
        estado["jarvis_hablando"] = False

        if not estado["microfono_bloqueado"]:
            estado["escuchando"] = True
            jarvis_ui.cambiar_color_texto("Esperando")
            jarvis_ui.actualizar_estado("Esperando comando...")
        else:
            estado["escuchando"] = False
            jarvis_ui.cambiar_color_texto("microfono_desactivado")
            jarvis_ui.actualizar_estado("🎙️ Micrófono desactivado")



def reproducir_snap_tony(hablar, jarvis_ui, estado):

    audio_tony = estado["recurso"]("tony_stark_snap.mp3")
    audio_explosion = estado["recurso"]("explosion.mp3")

    estado["efecto_explosion"]()

    if not os.path.exists(audio_tony):
        hablar("No encontré el audio de Tony Stark, señor.")
        return

    if not os.path.exists(audio_explosion):
        hablar("No encontré el audio de la explosión, señor.")
        return

    try:
        estado["jarvis_hablando"] = True
        estado["escuchando"] = False

        jarvis_ui.actualizar_estado("🫰 Yo soy Iron Man...")

        playsound(audio_tony)

        time.sleep(0.1)

        estado["efecto_explosion"]()

        jarvis_ui.actualizar_estado("💥")
        playsound(audio_explosion)

        estado["ultimo_audio"] = time.time()

    except Exception as e:
        print("❌ Error reproduciendo snap:", e)

    finally:
        estado["jarvis_hablando"] = False

        if not estado["microfono_bloqueado"]:
            estado["escuchando"] = True
            jarvis_ui.cambiar_color_texto("Esperando")
            jarvis_ui.actualizar_estado("Esperando comando...")
        else:
            estado["escuchando"] = False
            jarvis_ui.cambiar_color_texto("microfono_desactivado")
            jarvis_ui.actualizar_estado("🎙️ Micrófono desactivado")
            
def reproducir_efecto_personalizado(
    nombre_archivo, nombre_efecto, hablar, jarvis_ui, estado
):
    archivo = estado["recurso"](nombre_archivo)

    if not os.path.exists(archivo):
        hablar(f"No encontré el audio de {nombre_efecto}, señor.")
        return

    try:
        estado["jarvis_hablando"] = True
        estado["escuchando"] = False

        jarvis_ui.actualizar_estado(f"🔊 {nombre_efecto}")
        playsound(archivo)

        estado["ultimo_audio"] = time.time()
        time.sleep(0.3)

    except Exception as e:
        print(f"Error reproduciendo {nombre_efecto}:", e)

    finally:
        estado["jarvis_hablando"] = False

        if not estado["microfono_bloqueado"]:
            estado["escuchando"] = True
            jarvis_ui.cambiar_color_texto("Esperando")
            jarvis_ui.actualizar_estado("Esperando comando...")
        else:
            estado["escuchando"] = False
            jarvis_ui.cambiar_color_texto("microfono_desactivado")
            jarvis_ui.actualizar_estado("🎙️ Micrófono desactivado")