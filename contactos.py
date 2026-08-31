import json
import os
import unicodedata

def normalizar(texto):
    texto = texto.lower().strip()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto

ARCHIVO_CONTACTOS = os.path.join(
    os.path.dirname(__file__),
    "contactos.json"
)


def cargar_contactos():

    if not os.path.exists(ARCHIVO_CONTACTOS):
        return []

    with open(
        ARCHIVO_CONTACTOS,
        "r",
        encoding="utf-8"
    ) as archivo:

        return json.load(archivo)


def buscar_contacto(nombre):

    nombre = normalizar(nombre)

    contactos = cargar_contactos()

    for contacto in contactos:

        if normalizar(contacto["nombre"]) == nombre:
            return contacto["telefono"]

    return None


def agregar_contacto(nombre, telefono):

    contactos = cargar_contactos()

    contactos.append({

        "nombre": nombre,
        "telefono": telefono

    })

    with open(
        ARCHIVO_CONTACTOS,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            contactos,
            archivo,
            indent=4,
            ensure_ascii=False
        )


def eliminar_contacto(nombre):

    contactos = cargar_contactos()

    contactos = [

        c for c in contactos

        if c["nombre"].lower() != nombre.lower()

    ]

    with open(
        ARCHIVO_CONTACTOS,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            contactos,
            archivo,
            indent=4,
            ensure_ascii=False
        )


def listar_contactos():

    return cargar_contactos()