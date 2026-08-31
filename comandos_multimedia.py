import comandos_camara
from comandos_whatsapp import enviar_archivo_whatsapp


def tomar_foto_y_enviar(hablar, contacto, mensaje=""):

    # 📸 Tomar foto
    ruta = comandos_camara.tomar_foto(hablar)

    if ruta is None:
        hablar("No pude tomar la fotografía.")
        return

    # 📤 Enviar por WhatsApp
    enviar_archivo_whatsapp(
        hablar,
        contacto,
        ruta,
        mensaje
    )
    
def grabar_video_y_enviar(hablar, contacto, duracion=20, mensaje=""):

    ruta = comandos_camara.grabar_video(
        hablar,
        duracion
    )

    if ruta is None:
        hablar("No pude grabar el video.")
        return

    enviar_archivo_whatsapp(
        hablar,
        contacto,
        ruta,
        mensaje
    )