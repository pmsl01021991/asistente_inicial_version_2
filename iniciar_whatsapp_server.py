import subprocess
import requests
import time
import os
import socket

VERSION_SERVIDOR = "1.1.0"
PUERTO = 3000

def cerrar_servidor_node():
    subprocess.run(
        ["taskkill", "/F", "/IM", "node.exe"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def servidor_activo():

    try:

        r = requests.get(
            "http://127.0.0.1:3000/status",
            timeout=2
        )

        if r.status_code != 200:
            return False

        datos = r.json()

        return datos.get("version") == VERSION_SERVIDOR

    except:
        return False


def esperar_servidor(timeout=30):

    inicio = time.time()

    while time.time() - inicio < timeout:

        try:

            r = requests.get(
                "http://127.0.0.1:3000/status",
                timeout=2
            )

            if r.status_code == 200:

                datos = r.json()

                if datos.get("version") == VERSION_SERVIDOR:
                    return True

        except:
            pass

        time.sleep(1)

    return False


def iniciar_servidor_whatsapp():

    if servidor_activo():

        print("Servidor de WhatsApp actualizado.")

        return True

    print("Reiniciando servidor de WhatsApp...")

    cerrar_servidor_node()

    time.sleep(2)

    import sys

    if getattr(sys, "frozen", False):
        ruta_actual = sys._MEIPASS
    else:
        ruta_actual = os.path.dirname(os.path.abspath(__file__))

    carpeta_node = os.path.join(
        ruta_actual,
        "whatsapp-server"
    )

    startupinfo = subprocess.STARTUPINFO()

    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    subprocess.Popen(
        ["node", "server.js"],
        cwd=carpeta_node,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    print("Iniciando servidor de WhatsApp...")

    if esperar_servidor():

        print("Servidor listo.")

        return True

    print("No fue posible iniciar el servidor.")

    return False