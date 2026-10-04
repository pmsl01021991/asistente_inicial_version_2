import cv2
import time

modo_camara_activo = False

ultima_deteccion = set()
ultima_vision = []

def modo_vision_jarvis(hablar):
    
    from ultralytics import YOLO

    modelo = YOLO("yolov8s.pt")

    global modo_camara_activo, ultima_deteccion, ultima_vision

    modo_camara_activo = True
    ultima_deteccion.clear()

    hablar("Modo visión activado señor")

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        hablar("No pude abrir la cámara señor")
        modo_camara_activo = False
        return

    while modo_camara_activo:

        ret, frame = cap.read()
        if not ret:
            break

        resultados = modelo(frame)

        objetos_detectados = []

        for r in resultados:
            for box in r.boxes:
                clase = int(box.cls[0])
                nombre = modelo.names[clase]
                objetos_detectados.append(nombre)
        if objetos_detectados:
            objetos_unicos = list(set(objetos_detectados))
            ultima_vision.clear()
            ultima_vision.extend(objetos_unicos)

        # 🔥 TRADUCCIONES (DENTRO DEL WHILE)
        traducciones = {
            "person": "persona",
            "bicycle": "bicicleta",
            "car": "carro",
            "motorcycle": "motocicleta",
            "airplane": "avión",
            "bus": "bus",
            "train": "tren",
            "truck": "camión",
            "boat": "bote",
            "traffic light": "semáforo",
            "fire hydrant": "hidrante",
            "stop sign": "señal de pare",
            "parking meter": "parquímetro",
            "bench": "banca",
            "bird": "pájaro",
            "cat": "gato",
            "dog": "perro",
            "horse": "caballo",
            "sheep": "oveja",
            "cow": "vaca",
            "elephant": "elefante",
            "bear": "oso",
            "zebra": "cebra",
            "giraffe": "jirafa",
            "backpack": "mochila",
            "umbrella": "paraguas",
            "handbag": "bolso",
            "tie": "corbata",
            "suitcase": "maleta",
            "frisbee": "frisbee",
            "skis": "esquís",
            "snowboard": "snowboard",
            "sports ball": "pelota",
            "kite": "cometa",
            "baseball bat": "bate",
            "baseball glove": "guante de béisbol",
            "skateboard": "patineta",
            "surfboard": "tabla de surf",
            "tennis racket": "raqueta de tenis",
            "bottle": "botella",
            "wine glass": "copa de vino",
            "cup": "taza",
            "fork": "tenedor",
            "knife": "cuchillo",
            "spoon": "cuchara",
            "bowl": "tazón",
            "banana": "plátano",
            "apple": "manzana",
            "sandwich": "sándwich",
            "orange": "naranja",
            "broccoli": "brócoli",
            "carrot": "zanahoria",
            "hot dog": "hot dog",
            "pizza": "pizza",
            "donut": "dona",
            "cake": "pastel",
            "chair": "silla",
            "couch": "sofá",
            "potted plant": "planta",
            "bed": "cama",
            "dining table": "mesa",
            "toilet": "inodoro",
            "tv": "televisor",
            "laptop": "laptop",
            "mouse": "mouse",
            "remote": "control remoto",
            "keyboard": "teclado",
            "cell phone": "teléfono",
            "microwave": "microondas",
            "oven": "horno",
            "toaster": "tostadora",
            "sink": "lavadero",
            "refrigerator": "refrigeradora",
            "book": "libro",
            "clock": "reloj",
            "vase": "florero",
            "scissors": "tijeras",
            "teddy bear": "oso de peluche",
            "hair drier": "secadora de cabello",
            "toothbrush": "cepillo de dientes"
        }

        
        # 🔥 detectar objetos nuevos (SIN HABLAR)
        for obj in objetos_detectados:
            if obj not in ultima_deteccion:
                ultima_deteccion.add(obj)

        # 🔥 lógica de mano (SIN HABLAR)
        if "person" in objetos_detectados:
            objetos_sin_persona = [o for o in objetos_detectados if o != "person"]


        # 🔥 MOSTRAR CÁMARA (también dentro del while)
        annotated = resultados[0].plot()
        cv2.imshow("Jarvis Vision", annotated)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    
    modo_camara_activo = False

    hablar("Modo visión finalizado señor")


# ===============================
# 📸 TOMAR FOTO
# ===============================
def tomar_foto(hablar):

    hablar("Preparando cámara señor")

    cap = cv2.VideoCapture(
        0,
        cv2.CAP_DSHOW
    )

    if not cap.isOpened():
        hablar("No pude abrir la cámara señor")
        return None

    time.sleep(2)

    ret, frame = cap.read()

    if ret:

        nombre = f"foto_jarvis_{int(time.time())}.jpg"

        cv2.imwrite(nombre, frame)

        hablar("Foto tomada señor")

        cap.release()
        cv2.destroyAllWindows()

        return nombre

    else:

        hablar("No pude capturar la imagen señor")

        cap.release()
        cv2.destroyAllWindows()

        return None

def grabar_video(hablar, duracion=20):

    import subprocess
    import os
    import time
    import cv2

    hablar(f"Grabando video durante {duracion} segundos señor")

    nombre = f"video_jarvis_{int(time.time())}.mp4"

    ffmpeg = os.path.join(
        os.path.dirname(__file__),
        "ffmpeg",
        "ffmpeg.exe"
    )

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        hablar("No pude abrir la cámara señor")
        return None

    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 30

    comando = [
        ffmpeg,
        "-y",

        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-pix_fmt", "bgr24",
        "-s", f"{ancho}x{alto}",
        "-r", str(fps),
        "-i", "-",

        "-f", "dshow",
        "-i", "audio=Microphone Array (AMD Audio Device)",

        "-map", "0:v:0",
        "-map", "1:a:0",

        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",

        "-c:a", "aac",
        "-b:a", "192k",

        "-shortest",
        nombre
    ]

    proceso = subprocess.Popen(
        comando,
        stdin=subprocess.PIPE
    )

    inicio = time.time()

    while time.time() - inicio < duracion:

        ret, frame = cap.read()

        if not ret:
            break

        proceso.stdin.write(frame.tobytes())

        cv2.imshow("Grabando Video - Jarvis", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    proceso.stdin.close()
    proceso.wait()

    hablar("Grabación finalizada señor")

    return nombre
    