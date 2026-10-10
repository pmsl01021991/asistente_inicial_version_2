#  COMANDO PARA CONVERTIR EN .EXE


python -m PyInstaller --onedir --windowed --clean --icon=jarvis.ico --name Jarvis --add-data "jarvis4.gif;." --add-data "contactos.json;." --add-data "yolov8s.pt;." --add-data "modelos;modelos" --add-data "ffmpeg;ffmpeg" --add-data "whatsapp-server-dist;whatsapp-server" --collect-all PIL --collect-all cv2 --collect-all ultralytics --collect-all torch --collect-all speech_recognition --collect-all cryptography --collect-all requests --collect-all pygame --collect-all edge_tts --collect-all pyaudio --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=PIL.ImageTk --hidden-import=PIL.ImageSequence --hidden-import=cv2 --hidden-import=ultralytics --hidden-import=speech_recognition --hidden-import=pyautogui --hidden-import=pyperclip --hidden-import=requests --hidden-import=cryptography --hidden-import=cryptography.fernet --hidden-import=edge_tts --hidden-import=pygame --hidden-import=pyaudio asistente2.py



# 🔧 Soluciones y mantenimiento de Jarvis

Este documento contiene las soluciones realizadas para configurar y reparar Jarvis
después de mover/clonar el proyecto a otra computadora.

---

# 1. 📦 Verificar Node.js y npm

El servidor de WhatsApp utiliza Node.js.

Verificar:

```powershell
node -v
npm -v

En la PC actual:
Node: v24.21.0
npm: 11.19.0

2. 📱 Servidor de WhatsApp
El servidor se encuentra en:
whatsapp-server/

Archivos principales:
whatsapp-server/
├── server.js
├── package.json
├── package-lock.json
├── node_modules/
├── .wwebjs_auth/
└── .wwebjs_cache/

El servidor utiliza:
whatsapp-web.js
Express
Puppeteer

Puerto utilizado:
3000

3. 📥 Instalar dependencias del servidor
Si se clona el proyecto nuevamente y no existe node_modules:
Entrar a:
cd C:\PROYECTOS\asistente_inicial_version_2\whatsapp-server

Instalar:
npm install

Verificar WhatsApp Web JS:
npm list whatsapp-web.js puppeteer puppeteer-core

4. ⚠️ Problema de WhatsApp Web después de clonar el proyecto
Síntoma:
ProtocolError: Protocol error (Runtime.callFunctionOn):
Execution context was destroyed.

El servidor podía iniciar, pero WhatsApp Web fallaba al inicializar.
La causa fue una sesión/cache antigua de WhatsApp Web incompatible con la nueva computadora.
Solución
NO eliminar directamente las carpetas.
Renombrarlas:
.wwebjs_auth

por:
.wwebjs_auth_backup

Y:
.wwebjs_cache

por:
.wwebjs_cache_backup

Después iniciar nuevamente el servidor:
node server.js

Aparecerá un código QR.
Escanearlo desde WhatsApp.
Cuando aparezca:
✅ WhatsApp autenticado.
✅ WhatsApp conectado correctamente.

el servidor está funcionando.
5. 🔄 Reiniciar completamente el servidor Node
Si se modifica código dentro de:
node_modules/whatsapp-web.js/

y Jarvis continúa usando el comportamiento anterior, significa que Node todavía tiene cargada la versión anterior.
Cerrar Node:
taskkill /F /IM node.exe

Después volver a iniciar Jarvis normalmente desde VS Code con:
▶ Ejecutar

6. 🐙 Git y sesión de WhatsApp
Las carpetas de sesión de WhatsApp NO deben subirse a GitHub.
Agregar al .gitignore:
# Sesión de WhatsApp
whatsapp-server/.wwebjs_auth/
whatsapp-server/.wwebjs_cache/
whatsapp-server/.wwebjs_auth_backup/

# VS Code
.vscode/

También se utiliza:
node_modules/

7. 🧹 Si Git ya estaba siguiendo .wwebjs_auth
Si Git ya había agregado las carpetas antes de ponerlas en .gitignore:
git rm -r --cached --ignore-unmatch whatsapp-server/.wwebjs_auth

git rm -r --cached --ignore-unmatch whatsapp-server/.wwebjs_cache

Después:
git add .gitignore

Verificar:
git status

8. 📤 Guardar cambios en GitHub
Después de solucionar cambios importantes:
git add .

git commit -m "Solucionar servidor de WhatsApp y actualizar gitignore"

git push origin main

9. 📸 Problema al enviar fotografías por WhatsApp
Al enviar una fotografía aparecía:
Código HTTP: 500

y:
Data passed to getter must include an id property

El problema estaba relacionado con whatsapp-web.js y el objeto interno:
__x_id

10. 🔧 Solución para envío de fotografías
Archivo:
whatsapp-server/node_modules/whatsapp-web.js/src/util/Injected/Utils.js

Buscar la construcción del objeto:
const message = {
    ...
};

Justo después de cerrar el objeto agregar:
delete message.__x_id;

Debe quedar:
const message = {
    ...
};

delete message.__x_id;

Después de modificarlo es necesario cerrar el proceso Node:
taskkill /F /IM node.exe

Y volver a iniciar Jarvis.
11. 🎥 Problema al grabar videos
Inicialmente aparecía:
[WinError 2] El sistema no puede encontrar el archivo especificado

La causa era que Jarvis buscaba FFmpeg dentro del proyecto:
ffmpeg/ffmpeg.exe

pero el archivo no existía.
12. 🎬 Instalar FFmpeg
Instalar mediante Winget:
winget install Gyan.FFmpeg

Verificar:
ffmpeg -version

Verificar dónde está instalado:
where.exe ffmpeg

13. 📁 Copiar FFmpeg al proyecto
Jarvis utiliza FFmpeg desde:
C:\PROYECTOS\asistente_inicial_version_2\ffmpeg\ffmpeg.exe

Verificar:
Test-Path .\ffmpeg\ffmpeg.exe

Debe devolver:
True

También se puede comprobar:
.\ffmpeg\ffmpeg.exe -version

14. 🎥 Problema de cámara después de cambiar de computadora
La grabación original utilizaba:
Integrated Camera

pero la nueva computadora tenía:
HP True Vision FHD Camera

El micrófono era:
Microphone Array (AMD Audio Device)

Para verificar dispositivos DirectShow:
ffmpeg -list_devices true -f dshow -i dummy

Dispositivos encontrados:
HP True Vision FHD Camera
Microphone Array (AMD Audio Device)

15. ⚠️ Problema de cámara ocupada
Inicialmente FFmpeg intentaba abrir directamente:
video=HP True Vision FHD Camera

mientras OpenCV también utilizaba la cámara.
Esto provocaba:
Error during demuxing: I/O error

y:
Output file is empty

16. ✅ Solución definitiva para grabar video
No eliminar OpenCV.
OpenCV se mantiene porque Jarvis necesita mostrar la ventana de cámara.
La solución fue:
OpenCV
   ↓
captura la cámara
   ↓
frames BGR
   ↓
FFmpeg por stdin
   ↓
MP4

Mientras FFmpeg obtiene el audio directamente del micrófono:
Microphone Array (AMD Audio Device)
              ↓
            FFmpeg

De esta manera OpenCV y FFmpeg no intentan abrir la cámara al mismo tiempo.
17. 🎥 Configuración actual de grabación
En:
comandos_camara.py

La función:
grabar_video()


utiliza:
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)


FFmpeg recibe el video:
"-f", "rawvideo","-vcodec", "rawvideo","-pix_fmt", "bgr24","-s", f"{ancho}x{alto}","-r", str(fps),"-i", "-",


Y el audio:
"-f", "dshow","-i", "audio=Microphone Array (AMD Audio Device)",


Se combinan:
"-map", "0:v:0","-map", "1:a:0",


Video:
"-c:v", "libx264","-preset", "veryfast","-pix_fmt", "yuv420p",


Audio:
"-c:a", "aac","-b:a", "192k",


Y es MUY IMPORTANTE mantener:
"-shortest",


para que FFmpeg termine cuando finaliza la grabación.
18. ⏱️ Duración de grabación
Python controla la duración mediante:
inicio = time.time()while time.time() - inicio < duracion:


Actualmente Jarvis llama:
grabar_video(    hablar,    contacto,    duracion=20)


por lo que la grabación está configurada para aproximadamente:
20 segundos

19. 📲 Flujo final para enviar video
Cuando Jarvis recibe:
Graba un video y mándalo a mamá

el flujo es:
🎤 Voz
 ↓
asistente2.py
 ↓
grabar_video_y_enviar()
 ↓
grabar_video()
 ↓
OpenCV captura cámara
 ↓
FFmpeg recibe video
 ↓
FFmpeg captura micrófono
 ↓
MP4 con video + audio
 ↓
WhatsApp Server
 ↓
whatsapp-web.js
 ↓
WhatsApp
 ↓
📱 Mamá recibe el video

20. ▶️ Cómo iniciar Jarvis normalmente
NO es necesario iniciar manualmente:
node server.js

para el uso normal.
Jarvis inicia automáticamente el servidor mediante:
iniciar_whatsapp_server.py

Por lo tanto, normalmente basta con ejecutar Jarvis desde VS Code:
▶ Ejecutar

21. 🚨 Si WhatsApp vuelve a fallar después de mover el proyecto
Orden recomendado:
1. Verificar Node
node -v

2. Instalar dependencias
cd C:\PROYECTOS\asistente_inicial_version_2\whatsapp-server
npm install

3. Si WhatsApp Web da error de sesión
Renombrar:
.wwebjs_auth

a:
.wwebjs_auth_backup

y:
.wwebjs_cache

a:
.wwebjs_cache_backup

4. Reiniciar Node
taskkill /F /IM node.exe

5. Ejecutar Jarvis desde VS Code
▶

6. Escanear QR si WhatsApp lo solicita.
22. 🚨 Si las fotografías vuelven a dar error 500
Revisar:
whatsapp-server/node_modules/whatsapp-web.js/src/util/Injected/Utils.js

Debe existir:
delete message.__x_id;

Después:
taskkill /F /IM node.exe

y volver a ejecutar Jarvis.
23. 🚨 Si el video vuelve a fallar
Primero comprobar FFmpeg:
.\ffmpeg\ffmpeg.exe -version

Comprobar cámara/micrófono:
ffmpeg -list_devices true -f dshow -i dummy

Verificar que existan:
HP True Vision FHD Camera
Microphone Array (AMD Audio Device)

Y revisar que comandos_camara.py utilice exactamente esos nombres.
24. ⚠️ IMPORTANTE
No modificar innecesariamente:
comandos_camara.py

si la grabación ya funciona.
No eliminar:
OpenCV

porque Jarvis utiliza la cámara mediante OpenCV.
No quitar:
"-shortest",


porque FFmpeg puede quedarse ejecutándose indefinidamente.
No subir a GitHub:
.wwebjs_auth/
.wwebjs_cache/

porque contienen la sesión de WhatsApp.
25. ✅ Estado final
Actualmente Jarvis tiene funcionando:
- ✅ Servidor Node.js
- ✅ WhatsApp Web
- ✅ Autenticación mediante QR
- ✅ Envío de mensajes
- ✅ Envío de fotografías
- ✅ Cámara HP True Vision FHD
- ✅ FFmpeg
- ✅ Grabación de video
- ✅ Audio del micrófono
- ✅ Video + audio en MP4
- ✅ Envío automático del video por WhatsApp
- ✅ Ejecución normal desde VS Code

**Este README te va a servir bastante cuando vuelvas a clonar el proyecto en otra PC**, porque ahí tienes no solo los comandos, sino **qué problema solucionaba cada comando**.