import json
import os
import sys
from cryptography.fernet import Fernet
import unicodedata

# --------------------------
# Carpeta donde guardar memoria
# --------------------------
if getattr(sys, "frozen", False):
    # Ejecutándose como .exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Ejecutándose como .py
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

historial_conversacion = []
memoria = {}

ARCHIVO_MEMORIA = os.path.join(BASE_DIR, "memoria_jarvis.json")
ARCHIVO_LLAVE = os.path.join(BASE_DIR, "clave_secreta.key")

print("BASE_DIR:", BASE_DIR)
print("ARCHIVO_MEMORIA:", ARCHIVO_MEMORIA)
print("ARCHIVO_LLAVE:", ARCHIVO_LLAVE)

# --------------------------
# 🔐 GENERAR O CARGAR LLAVE
# --------------------------
def cargar_o_crear_llave():
    if os.path.exists(ARCHIVO_LLAVE):
        with open(ARCHIVO_LLAVE, "rb") as f:
            return Fernet(f.read())
    else:
        key = Fernet.generate_key()
        with open(ARCHIVO_LLAVE, "wb") as f:
            f.write(key)
        return Fernet(key)

fernet = cargar_o_crear_llave()
            
# --------------------------
# 🔐 GUARDAR MEMORIA ENCRIPTADA
# --------------------------
def guardar_memoria():
    print("Guardando memoria en:", ARCHIVO_MEMORIA)
    data = {
        "memoria": memoria,
        "historial": historial_conversacion[-25:]
    }

    texto = json.dumps(data, ensure_ascii=False).encode()
    texto_encriptado = fernet.encrypt(texto)

    with open(ARCHIVO_MEMORIA, "wb") as f:
        f.write(texto_encriptado)

    print("🧠 Memoria guardada y encriptada correctamente.")

# --------------------------
# 🔐 CARGAR MEMORIA ENCRIPTADA
# --------------------------
def cargar_memoria():
    print("Cargando memoria desde:", ARCHIVO_MEMORIA)
    global memoria, historial_conversacion

    if not os.path.exists(ARCHIVO_MEMORIA):
        print("🧠 No hay memoria previa.")
        return

    try:
        with open(ARCHIVO_MEMORIA, "rb") as f:
            texto_encriptado = f.read()

        texto = fernet.decrypt(texto_encriptado)
        data = json.loads(texto.decode())

        memoria.clear()
        memoria.update(data.get("memoria", {}))

        historial_conversacion.clear()
        historial_conversacion.extend(data.get("historial", []))

        print("🧠 Memoria cargada:", memoria)

    except Exception as e:
        print("⚠️ Error cargando memoria:", e)
        memoria.clear()
        historial_conversacion.clear()
        
def analizar_y_guardar_info(texto):
    global memoria

    texto_original = texto.lower()

    texto_normalizado = ''.join(
        c for c in unicodedata.normalize('NFD', texto_original)
        if unicodedata.category(c) != 'Mn'
    )
    
        # Guardar memoria solamente con el comando "guarda:"
    if texto_normalizado.startswith("guarda:"):
        contenido = texto_original.split(":", 1)[1].strip()

        if contenido:
            memoria.setdefault("notas", []).append(contenido)
            guardar_memoria()
            print("🧠 Información guardada:", contenido)

        return

    # Nombre del usuario
    if "mi nombre es" in texto_normalizado:
        memoria["nombre_usuario"] = texto_original.split("mi nombre es", 1)[1].strip()

    # Nombres de familiares
    if "mi mama se llama" in texto_normalizado:
        memoria["nombre_mama"] = texto_original.split("se llama", 1)[1].strip()

    if "mi papa se llama" in texto_normalizado:
        memoria["nombre_papa"] = texto_original.split("se llama", 1)[1].strip()

    if "mi hermano se llama" in texto_normalizado:
        memoria["nombre_hermano"] = texto_original.split("se llama", 1)[1].strip()

    if "mi hermana se llama" in texto_normalizado:
        memoria["nombre_hermana"] = texto_original.split("se llama", 1)[1].strip()

    # Edad del usuario
    if "tengo" in texto_normalizado and "anos" in texto_normalizado:
        try:
            edad = next(int(s) for s in texto_normalizado.split() if s.isdigit())
            memoria["edad"] = edad
        except StopIteration:
            pass

    # Guardar cumpleaños
    if "mi cumpleanos es" in texto_normalizado:
        memoria["cumpleaños"] = texto_original.split("mi cumpleaños es", 1)[1].strip()

    # Guardar actividades
    if "recuerdame" in texto_normalizado or "recordarme" in texto_normalizado:
        if "que" in texto_normalizado:
            actividad = texto_original.split("que", 1)[1].strip()
            memoria.setdefault("actividades", []).append(actividad)

    # Guardar correos
    if "mi correo es" in texto_normalizado:
        correo = texto_original.replace("mi correo es", "").strip()
        memoria["correo"] = correo

    # Guardar contraseñas ENCRIPTADAS
    if "mi contrasena es" in texto_normalizado or "mi clave es" in texto_normalizado:
        clave = texto_original.split("es", 1)[1].strip()
        memoria["password"] = clave # se encripta automáticamente al guardar
  