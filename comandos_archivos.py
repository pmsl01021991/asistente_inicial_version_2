import os

from comandos_whatsapp import enviar_archivo_whatsapp


CARPETA_ARCHIVOS = os.path.join(
    os.path.dirname(__file__),
    "documentos"
)


EXTENSIONES_PERMITIDAS = (
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".txt",
    ".zip",
    ".rar",
    ".jpg",
    ".jpeg",
    ".png",
    ".mp4",
    ".avi",
    ".mov",
    ".mp3",
    ".wav"
)


def buscar_archivo(nombre):

    if not os.path.exists(CARPETA_ARCHIVOS):
        return None

    nombre = nombre.lower().strip()

    for archivo in os.listdir(CARPETA_ARCHIVOS):

        ruta = os.path.join(
            CARPETA_ARCHIVOS,
            archivo
        )

        if not os.path.isfile(ruta):
            continue

        if not archivo.lower().endswith(EXTENSIONES_PERMITIDAS):
            continue

        nombre_archivo = os.path.splitext(
            archivo
        )[0].lower()

        if nombre in nombre_archivo:

            return ruta

    return None


def procesar_archivo(hablar, comando):

    comando = comando.lower()

    comando = comando.replace(
        "jarvis",
        ""
    ).strip()

    comando = comando.replace(
        "envia",
        ""
    )

    comando = comando.replace(
        "manda",
        ""
    )

    comando = comando.replace(
        "enviar",
        ""
    )

    comando = comando.strip()

    if " a " not in comando:

        hablar("¿A quién desea enviar el archivo?")

        return

    partes = comando.rsplit(" a ", 1)

    nombre_archivo = partes[0].strip()

    contacto = partes[1].strip()

    ruta = buscar_archivo(
        nombre_archivo
    )

    if ruta is None:

        hablar(
            "No encontré ese archivo."
        )

        return

    hablar(
        f"Enviando {os.path.basename(ruta)} a {contacto}"
    )

    enviar_archivo_whatsapp(

        hablar,
        contacto,
        ruta

    )