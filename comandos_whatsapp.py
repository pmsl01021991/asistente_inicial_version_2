import requests
import speech_recognition as sr
import pyautogui
import pyperclip
import time
import os
from contactos import buscar_contacto
from PIL import Image
SERVIDOR_WHATSAPP = "http://localhost:3000"


def escuchar_whatsapp(duracion=20):

    r = sr.Recognizer()

    with sr.Microphone() as source:

        print("Escuchando respuesta de WhatsApp...")

        r.pause_threshold = 1.5
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True

        r.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = r.listen(source, timeout=7, phrase_time_limit=duracion)

            texto = r.recognize_google(audio, language="es-PE")

            print("WhatsApp escuchó:", texto)

            return texto.lower()

        except:
            return ""


def corregir_texto(texto):

    correcciones = {
        "maana": "mañana",
        "cumpleaos": "cumpleaños",
        "anos": "años",
        "feliz cumple": "feliz cumpleaños"
    }

    for e, c in correcciones.items():
        texto = texto.replace(e, c)

    return texto

def interpretar_whatsapp(comando):
    comando = comando.lower()

    if "dile a" in comando and "que" in comando:

        try:
            parte = comando.split("dile a")[1]

            contacto = parte.split("que")[0].strip()

            mensaje = parte.split("que")[1].strip()

            return contacto, mensaje

        except:
            return None, None

    return None, None


def enviar_whatsapp_web(hablar, contacto=None, mensaje=None):

    if contacto is None:
        hablar("¿A quién desea enviar el mensaje?")
        time.sleep(1.5)

        contacto = escuchar_whatsapp()

        if not contacto:
            hablar("No escuché el nombre.")
            return

    if mensaje is None:
        hablar("¿Qué mensaje desea enviar?")
        time.sleep(1.5)

        mensaje = escuchar_whatsapp()

        if not mensaje:
            hablar("No escuché el mensaje.")
            return

    mensaje = corregir_texto(mensaje)
    
    telefono = buscar_contacto(contacto)

    if telefono is None:
        hablar(f"No encontré el contacto {contacto}.")
        return

    try:

        respuesta = requests.post(
            f"{SERVIDOR_WHATSAPP}/send-message",
            json={
                "telefono": telefono,
                "mensaje": mensaje
            },
            timeout=15
        )

        if respuesta.status_code == 200:

            datos = respuesta.json()

            if datos["success"]:
                hablar("Mensaje enviado correctamente.")
            else:
                hablar("No pude enviar el mensaje.")

        else:
            hablar("Error de comunicación con el servidor.")

    except Exception as e:

        print(e)

        hablar("No pude conectarme al servidor de WhatsApp.")


def llamar_whatsapp(hablar):

    hablar("¿A quién desea llamar?")
    time.sleep(1.5)

    contacto = escuchar_whatsapp()

    if not contacto:
        hablar("No escuché el nombre.")
        return

    hablar(f"Llamando a {contacto}")

    os.system("start whatsapp:")
    time.sleep(8)

    pyautogui.hotkey("ctrl", "f")
    time.sleep(2)

    pyperclip.copy(contacto)
    pyautogui.hotkey("ctrl", "v")

    pyautogui.press("enter")

def enviar_archivo_whatsapp(hablar, contacto, ruta_imagen, mensaje=""):

    if not os.path.exists(ruta_imagen):
        hablar("No encontré la fotografía.")
        return

    telefono = buscar_contacto(contacto)

    if telefono is None:
        hablar(f"No encontré el contacto {contacto}.")
        return

    try:
        print("Contacto:", contacto)
        print("Teléfono:", telefono)
        print("Ruta:", os.path.abspath(ruta_imagen))

        respuesta = requests.post(
            f"{SERVIDOR_WHATSAPP}/send-file",
            json={
                "telefono": telefono,
                "ruta": os.path.abspath(ruta_imagen),
                "mensaje": mensaje
            },
            timeout=30
        )
        
        print("Código HTTP:", respuesta.status_code)
        print("Respuesta:", respuesta.text)

        if respuesta.status_code == 200:

            datos = respuesta.json()

            if datos["success"]:
                hablar("archivo envíado correctamente.")
            else:
                hablar("No pude enviar el archivo.")

        else:
            print("Código HTTP:", respuesta.status_code)
            print("Respuesta:", respuesta.text)
            hablar("Error de comunicación con el servidor.")

    except Exception as e:

        print(e)
        hablar("No pude conectarme al servidor de WhatsApp.")