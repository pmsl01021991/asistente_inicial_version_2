import speech_recognition as sr
import os
import sys
import time
import asyncio
import edge_tts
import datetime
import pygame
import threading
import unicodedata
from interfaz_jarvis import InterfazJarvisAnimada
from comandos_whatsapp import enviar_whatsapp_web, llamar_whatsapp, interpretar_whatsapp
from comandos_multimedia import (tomar_foto_y_enviar,grabar_video_y_enviar)
from comandos_sistema import (apagar_sistema, reiniciar_sistema, suspender_sistema, confirmar_accion_por_voz)
from ollama_manager import ollama
from memoria import (memoria, cargar_memoria, guardar_memoria, analizar_y_guardar_info, historial_conversacion)
import comandos_camara
import reconocimiento_facial
from iniciar_whatsapp_server import iniciar_servidor_whatsapp
from comandos_archivos import procesar_archivo
from seguridad_asistente import configurar_clave, verificar_clave, cargar_clave

escuchando = True
microfono_bloqueado = False
jarvis_hablando = False
pensando_ollama = False
ultimo_audio = 0
microfono_calibrado = False

def normalizar_texto(texto):
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto
    
def limpiar_texto(texto):
    return texto.replace("\n", " ").strip()[:500]

def corregir_texto(texto):
    texto = texto.lower()

    for mal, bien in memoria.get("correcciones", {}).items():
        texto = texto.replace(mal, bien)

    return texto

ULTIMA_INTERACCION = time.time()

def desactivar_microfono():
    global escuchando, microfono_bloqueado
    microfono_bloqueado = True
    escuchando = False
    jarvis_ui.cambiar_color_texto("microfono_desactivado")
    jarvis_ui.actualizar_estado("🎙️ Micrófono desactivado")
    hablar("Micrófono desactivado.")

def activar_microfono():
    global escuchando, microfono_bloqueado

    microfono_bloqueado = False
    escuchando = True

    jarvis_ui.cambiar_color_texto("microfono_activado")
    jarvis_ui.actualizar_estado("🎙️ Micrófono activado")

    hablar("Micrófono activado.")
    
    
def escuchar_comando(silencioso=False):
    global ultimo_audio, jarvis_hablando, microfono_calibrado, ULTIMA_INTERACCION

    # ⏳ Evitar capturar eco del propio audio
    if time.time() - ultimo_audio < 3.5:
        return ""

    # 🔇 Micrófono apagado
    if not escuchando:
        return ""

    with sr.Microphone() as source:
        # 🔥 Reinicia inactividad AL EMPEZAR a escuchar
        ULTIMA_INTERACCION = time.time()

        print("🎙️ Escuchando...")

        try:
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

            comando = recognizer.recognize_google(audio, language="es-PE")
            comando = corregir_texto(comando)
            jarvis_ui.cambiar_color_texto("escuchando")
            jarvis_ui.mostrar_texto_escuchado(comando)

            print(f"Usted dijo: {comando}")

            # 🔥 Reinicia inactividad AL CONFIRMAR voz
            ULTIMA_INTERACCION = time.time()

            return comando.lower()

        except sr.WaitTimeoutError:
            return ""

        except sr.UnknownValueError:
            return ""

        except sr.RequestError:
            if not silencioso:
                hablar("Señor, hubo un problema con el reconocimiento.")
            return ""
    
def ejecutar_comando(comando):
    comando = normalizar_texto(comando)
    
    
    # ==============================
    # RECONOCIMIENTO FACIAL
    # ==============================

    if "registrar mi rostro" in comando or "registrar rostro" in comando:
        try:
            reconocimiento_facial.registrar_rostro(hablar, nombre="Pablo")
        except Exception as e:
            print("Error en registro facial:", e)
            hablar("No pude completar el registro facial.")
        return

    elif "reconoce mi rostro" in comando or "reconocer mi rostro" in comando or \
         "quien esta frente a la camara" in comando:
        try:
            reconocimiento_facial.reconocer_rostro(hablar)
        except Exception as e:
            print("Error en reconocimiento facial:", e)
            hablar("Ocurrió un problema al reconocer el rostro.")
        return

    elif "cuantas personas hay" in comando or "cuantas personas ves" in comando:
        try:
            reconocimiento_facial.contar_personas(hablar)
        except Exception as e:
            print("Error al contar rostros:", e)
            hablar("No pude contar los rostros.")
        return

    if "establecer clave" in comando:
        configurar_clave(hablar, escuchar_comando)
        return

    # 🎙️ ACTIVAR / DESACTIVAR MICRÓFONO
    if "desactivar microfono" in comando or "desactiva el microfono "in comando:

        desactivar_microfono()
        return

    elif "activa el microfono" in comando or \
         "activar el microfono" in comando or \
         "enciende el microfono" in comando:

        activar_microfono()
        return
    elif "que hora es" in comando or "dime la hora" in comando:
        hora = datetime.datetime.now().strftime("%H:%M")
        hablar(f"Son las {hora}")
        return

    elif "que dia es hoy" in comando:
        fecha = datetime.datetime.now().strftime("%d de %B del %Y")
        hablar(f"Hoy es {fecha}")
        return
    
    elif "toma una foto y mandalo a" in comando or "toma una foto y mandarlo a" in comando:

        try:

            contacto = comando.lower()

            contacto = contacto.replace(
                "toma una foto y mandalo a",
                ""
            )
            
            contacto = contacto.replace(
                "toma una foto y mandarlo a",
                ""
            )

            contacto = contacto.strip()

            tomar_foto_y_enviar(
                hablar,
                contacto
            )

        except Exception as e:
            hablar("No pude enviar la fotografía.")
            print(e)

        return
    
    contacto, mensaje = interpretar_whatsapp(comando)

    if contacto and mensaje:
        hablar(f"Enviando mensaje a {contacto}")
        enviar_whatsapp_web(hablar, contacto, mensaje)
        return

    elif "jarvis abrir whatsapp" in comando or \
        "abre whatsapp" in comando or \
        "inicia whatsapp" in comando:

        hablar("Abriendo WhatsApp señor.")

        os.system("start whatsapp:")

        return
#----LIMPIAR PAPELERA----

    elif "vaciar papelera" in comando or "limpiar papelera" in comando:
        hablar("Vaciando la papelera de reciclaje, señor.")
        os.system('PowerShell -Command "Clear-RecycleBin -Force"')
        hablar("Papelera limpia señor.")
        return
    elif "apagar el sistema" in comando or "apagar computadora" in comando:
        confirmar_accion_por_voz(
            "apagar",
            hablar,
            escuchar_comando,
            jarvis_ui
        )

    elif "reiniciar el sistema" in comando or "reiniciar computadora" in comando:
        confirmar_accion_por_voz(
            "reiniciar",
            hablar,
            escuchar_comando,
            jarvis_ui
        )

    elif "suspender el sistema" in comando or "modo suspensión" in comando:
        confirmar_accion_por_voz(
            "suspender",
            hablar,
            escuchar_comando,
            jarvis_ui
        )
        
    elif "gracias" in comando or "gracias jarvis" in comando:
        hablar("Para servirle señor.")
        return
        
    # 👋 SALIR
    elif "salir" in comando or "cerrar" in comando:
        hablar("Hasta luego señor.")
        os._exit(0)
        return
    
    elif "jarvis visión" in comando or "jarvis vision" in comando:

        if comandos_camara.modo_camara_activo:
            hablar("La visión ya está activa señor")
            return

        threading.Thread(
            target=comandos_camara.modo_vision_jarvis,
            args=(hablar,),
            daemon=True
        ).start()

        return
    
    elif "detener vision" in comando or "detener vision" in comando:

        comandos_camara.modo_camara_activo = False
        hablar("Cerrando visión señor")
        return
    
    elif "toma un selfi" in comando or "tomame una selfi" in comando:

        comandos_camara.tomar_foto(hablar)
        return
    
    elif "graba un video y mandalo a" in comando or \
        "graba un video y mandarlo a" in comando:

        contacto = comando.lower()

        contacto = contacto.replace(
            "graba un video y mandalo a",
            ""
        )

        contacto = contacto.replace(
            "graba un video y mandarlo a",
            ""
        )

        contacto = contacto.strip()

        grabar_video_y_enviar(
            hablar,
            contacto,
            duracion=20
        )

        return
    
    elif "grabar video" in comando:

        comandos_camara.grabar_video(hablar)
        return
    
    elif "envia" in comando or "manda" in comando:

        procesar_archivo(
            hablar,
            comando
        )

        return

    # 🧠 RESPUESTA NORMAL CON OLLAMA
    else:
        jarvis_ui.cambiar_color_texto("pensando")
        jarvis_ui.actualizar_estado("🧠 Pensando...")
        
        analizar_y_guardar_info(comando)
        guardar_memoria()

        respuesta = ollama.preguntar(comando)

        jarvis_ui.cambiar_color_texto("hablando")
        jarvis_ui.actualizar_estado("🗣️ Hablando...")

        hablar(respuesta, mostrar=False)

        jarvis_ui.cambiar_color_texto("Esperando")
        jarvis_ui.actualizar_estado("Esperando comando...")
    
ACTIVADORES = (
    "jarvis",
    "hola jarvis",
    "oye jarvis",
    "jarvis estás ahí",
    "jarvis estas ahi",
)

recognizer = sr.Recognizer()
pygame.mixer.init()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 1.8
recognizer.non_speaking_duration = 0.8
recognizer.operation_timeout = 5

def recurso(ruta_relativa):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, ruta_relativa)

def hablar(texto, mostrar=False):
    if mostrar:
        print("Jarvis:", texto)

    asyncio.run(_hablar(texto))

async def _hablar(texto):
    archivo = "voz.mp3"

    communicate = edge_tts.Communicate(
        text=texto,
        voice="es-PE-CamilaNeural",
        rate="+15%"

    )

    await communicate.save(archivo)
    pygame.mixer.music.load(archivo)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.01)
    pygame.mixer.music.unload()
    os.remove(archivo)
    
def iniciar_jarvis():
    cargar_memoria()
    
    
    # AUTENTICACION FACIAL Y CLAVE DE VOZ
    rostro_validado = False

    try:
        rostro_registrado = (
            os.path.exists(reconocimiento_facial.ARCHIVO_ROSTRO)
            and os.path.exists(reconocimiento_facial.ARCHIVO_NOMBRES)
        )

        if not rostro_registrado:
            hablar("No hay un rostro registrado. Vamos a registrarlo.")

            rostro_validado = reconocimiento_facial.registrar_rostro(
                hablar,
                nombre="Pablo"
            )

        else:
            nombre_reconocido = reconocimiento_facial.reconocer_rostro(hablar)
            rostro_validado = nombre_reconocido == "Pablo"

    except Exception as e:
        print("Error en autenticación facial:", e)
        hablar("No pude verificar el rostro. Usaremos la clave de voz.")

    if not rostro_validado:
        if not cargar_clave():
            hablar("No hay una clave configurada. Vamos a establecer una nueva clave.")

            if not configurar_clave(hablar, escuchar_comando):
                hablar("No se pudo establecer la clave. El asistente se cerrará.")
                os._exit(0)

        else:
            if not verificar_clave(hablar, escuchar_comando):
                os._exit(0)

    else:
        print("Autenticación facial correcta.")


    hora_actual = datetime.datetime.now().hour

    if hora_actual < 12:
        saludo = "Buenos días, señor."
    elif hora_actual < 18:
        saludo = "Buenas tardes, señor."
    else:
        saludo = "Buenas noches, señor."

    hablar(f"{saludo} Bienvenido. Jarvis listo para asistirle.")

    with sr.Microphone() as source:

        print("Calibrando micrófono...")
        recognizer.adjust_for_ambient_noise(source, duration=2)

        while True:

            try:

                if not escuchando:

                    try:

                        audio = recognizer.listen(
                            source,
                            timeout=3,
                            phrase_time_limit=3
                        )

                        try:
                            texto_activador = normalizar_texto(
                                recognizer.recognize_google(
                                    audio,
                                    language="es-PE"
                                )
                            )
                        except:
                            texto_activador = ""

                        if any(a in texto_activador for a in ACTIVADORES):
                            activar_microfono()

                    except:
                        pass

                    continue

                print("🎤 Escuchando...")

                jarvis_ui.cambiar_color_texto("escuchando")
                jarvis_ui.actualizar_estado("🎤 Escuchando...")

                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=8
                )

                try:
                    texto = normalizar_texto(
                        recognizer.recognize_google(
                            audio,
                            language="es-PE"
                        )
                    )
                except sr.UnknownValueError:
                    texto = ""

                except sr.RequestError:
                    texto = ""

                print("Tú:", texto)

                if not texto:
                    print("No detectó texto.")
                    jarvis_ui.actualizar_estado("No entendí, intenta otra vez.")
                    continue
                

                jarvis_ui.mostrar_texto_escuchado(texto)

                ejecutar_comando(texto)

            except sr.WaitTimeoutError:
                pass

            except Exception as e:
                print("Error:", e)
                jarvis_ui.actualizar_estado("No entendí, intenta otra vez.")

if not iniciar_servidor_whatsapp():
    print("No se pudo iniciar el servidor de WhatsApp.")
            
jarvis_ui = InterfazJarvisAnimada(recurso)

threading.Thread(
    target=iniciar_jarvis,
    daemon=True
).start()

jarvis_ui.ventana.mainloop()