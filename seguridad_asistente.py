import json
import unicodedata
import sys
import os

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ARCHIVO_CLAVE = os.path.join(BASE_DIR, "clave_asistente.json")


def normalizar_clave(texto):
    texto = texto.lower().strip()

    texto = ''.join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )

    return texto


def cargar_clave():
    if not os.path.exists(ARCHIVO_CLAVE):
        return None

    try:
        with open(ARCHIVO_CLAVE, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        return datos.get("clave")

    except Exception:
        return None


def guardar_clave(clave):
    clave = normalizar_clave(clave)

    with open(ARCHIVO_CLAVE, "w", encoding="utf-8") as archivo:
        json.dump(
            {"clave": clave},
            archivo,
            ensure_ascii=False,
            indent=4
        )


def configurar_clave(hablar, escuchar_comando):
    hablar("Diga la nueva clave por favor.")

    clave = escuchar_comando(silencioso=True)

    if not clave:
        hablar("No pude escuchar la clave.")
        return False

    guardar_clave(clave)

    hablar("Clave guardada correctamente señor.")
    return True


def verificar_clave(hablar, escuchar_comando):

    clave_guardada = cargar_clave()

    if not clave_guardada:
        hablar("No hay una clave configurada. Primero debe establecer una clave.")
        return False

    for intento in range(3):

        hablar("Para activar este asistente diga la clave por favor.")

        clave_ingresada = escuchar_comando(silencioso=True)

        if clave_ingresada:
            clave_ingresada = normalizar_clave(clave_ingresada)

            if clave_ingresada == clave_guardada:
                return True

        if intento < 2:
            hablar("Clave incorrecta, vuelva a decir la clave por favor.")

    hablar("Clave incorrecta. Se alcanzó el máximo de intentos. El asistente se desactivará.")

    return False