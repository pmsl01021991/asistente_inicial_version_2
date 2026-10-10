import os
import time
import cv2
import json
import numpy as np
import sys

if getattr(sys, "frozen", False):
    CARPETA_BASE = os.path.dirname(sys.executable)
else:
    CARPETA_BASE = os.path.dirname(os.path.abspath(__file__))

CARPETA_DATOS = os.path.join(
    CARPETA_BASE,
    "datos_faciales"
)

ARCHIVO_ROSTRO = os.path.join(CARPETA_DATOS, "rostro.yml")
ARCHIVO_NOMBRES = os.path.join(CARPETA_DATOS, "nombres.json")

UMBRAL_RECONOCIMIENTO = 65


def _preparar_carpeta():
    os.makedirs(CARPETA_DATOS, exist_ok=True)



def _detector_rostros():
    ruta = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "modelos",
        "haarcascade_frontalface_default.xml"
    )

    if not os.path.isfile(ruta):
        raise FileNotFoundError(
            f"No se encontró el detector facial: {ruta}"
        )

    detector = cv2.CascadeClassifier(ruta)

    if detector.empty():
        raise RuntimeError(
            f"No se pudo cargar el detector facial: {ruta}"
        )

    return detector


def _abrir_camara():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        cap.release()
        raise RuntimeError("No se pudo abrir la cámara.")

    return cap



def registrar_rostro(hablar, nombre="Pablo"):
    _preparar_carpeta()

    if os.path.exists(ARCHIVO_ROSTRO) and os.path.exists(ARCHIVO_NOMBRES):
        hablar("Ya existe un rostro registrado.")
        return True

    hablar("Voy a registrar tu rostro. Mira directamente a la cámara.")


    detector = _detector_rostros()
    cap = _abrir_camara()
    muestras = []
    inicio = time.time()
    ultimo_aviso = 0

    try:
        while time.time() - inicio < 20 and len(muestras) < 40:
            ret, frame = cap.read()

            if not ret:
                break

            gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rostros = detector.detectMultiScale(
                gris,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(100, 100)
            )

            for (x, y, w, h) in rostros:
                cv2.rectangle(
                    frame, (x, y), (x + w, y + h),
                    (0, 255, 0), 2
                )

                rostro = gris[y:y + h, x:x + w]
                rostro = cv2.resize(rostro, (200, 200))

                if len(muestras) == 0 or time.time() - ultimo_aviso >= 0.35:
                    muestras.append(rostro.copy())
                    ultimo_aviso = time.time()

                break

            cv2.putText(
                frame,
                f"Muestras: {len(muestras)}/40",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.imshow("Registro facial - JARVIS", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

    if len(muestras) < 10:
        hablar("No pude registrar suficientes muestras. Intenta de nuevo.")
        return False

    reconocedor = cv2.face.LBPHFaceRecognizer_create()
    etiquetas = np.array([1] * len(muestras), dtype=np.int32)
    reconocedor.train(muestras, etiquetas)
    reconocedor.write(ARCHIVO_ROSTRO)

    with open(ARCHIVO_NOMBRES, "w", encoding="utf-8") as archivo:
        json.dump({"1": nombre}, archivo, ensure_ascii=False, indent=4)

    hablar("Registro facial completado.")
    return True


def reconocer_rostro(hablar):
    _preparar_carpeta()

    if not os.path.exists(ARCHIVO_ROSTRO) or not os.path.exists(ARCHIVO_NOMBRES):
        hablar("Primero debes registrar tu rostro.")
        return None

    reconocedor = cv2.face.LBPHFaceRecognizer_create()
    reconocedor.read(ARCHIVO_ROSTRO)

    with open(ARCHIVO_NOMBRES, "r", encoding="utf-8") as archivo:
        nombres = json.load(archivo)

    detector = _detector_rostros()
    cap = _abrir_camara()
    resultado_final = None
    conteo_rostros = 0
    inicio = time.time()
    nombre_candidato = None
    confirmaciones = 0

    hablar("Analizando el rostro. Mira a la cámara.")

    try:
        while time.time() - inicio < 10:
            ret, frame = cap.read()

            if not ret:
                break

            gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rostros = detector.detectMultiScale(
                gris,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(100, 100)
            )

            
            conteo_rostros = len(rostros)

            if conteo_rostros == 0:
                nombre_candidato = None
                confirmaciones = 0
                resultado_final = None

            for (x, y, w, h) in rostros:
                rostro = cv2.resize(
                    gris[y:y + h, x:x + w],
                    (200, 200)
                )

                etiqueta, confianza = reconocedor.predict(rostro)

                if (
                    confianza < UMBRAL_RECONOCIMIENTO
                    and str(etiqueta) in nombres
                ):
                    nombre = nombres[str(etiqueta)]

                    if nombre == nombre_candidato:
                        confirmaciones += 1
                    else:
                        nombre_candidato = nombre
                        confirmaciones = 1

                    if confirmaciones >= 5:
                        resultado_final = nombre

                    texto = f"{nombre} ({confianza:.0f})"
                    color = (0, 255, 0)

                else:
                    nombre_candidato = None
                    confirmaciones = 0
                    resultado_final = None
                    texto = "Desconocido"
                    color = (0, 0, 255)

                cv2.rectangle(
                    frame, (x, y), (x + w, y + h), color, 2
                )
                cv2.putText(
                    frame, texto, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2
                )


            cv2.imshow("Reconocimiento facial - JARVIS", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

    if conteo_rostros == 0:
        hablar("No detecté ningún rostro.")
    elif resultado_final:
        hablar(f"El rostro registrado corresponde a {resultado_final}.")
    else:
        hablar("Detecté un rostro, pero no pude confirmar su identidad.")

    return resultado_final


def contar_personas(hablar):
    detector = _detector_rostros()
    cap = _abrir_camara()
    conteo = 0

    hablar("Voy a contar las personas visibles.")

    try:
        ret, frame = cap.read()

        if not ret:
            hablar("No pude capturar la imagen.")
            return 0

        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = detector.detectMultiScale(
            gris,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(100, 100)
        )

        conteo = len(rostros)

        for (x, y, w, h) in rostros:
            cv2.rectangle(
                frame, (x, y), (x + w, y + h), (0, 255, 0), 2
            )

        cv2.putText(
            frame,
            f"Rostros detectados: {conteo}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.imshow("Conteo facial - JARVIS", frame)
        cv2.waitKey(2000)

    finally:
        cap.release()
        cv2.destroyAllWindows()

    if conteo == 1:
        hablar("Detecté un rostro.")
    else:
        hablar(f"Detecté {conteo} rostros.")

    return conteo
