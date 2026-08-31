import tkinter as tk
from PIL import Image, ImageTk, ImageSequence


class InterfazJarvisAnimada:
    def __init__(self, recurso):
        self.recurso = recurso

        self.ventana = tk.Tk()
        self.ventana.title("JARVIS HUD")

        ancho, alto = 400, 400
        self.centrar_ventana_en_pantalla(ancho, alto)

        self.ventana.resizable(False, False)
        self.ventana.overrideredirect(True)
        self.ventana.wm_attributes("-transparentcolor", "black")
        self.ventana.configure(bg="black")
        self.ventana.update_idletasks()

        self.gif = Image.open(self.recurso("jarvis4.gif"))
        self.frames = [
            ImageTk.PhotoImage(frame.copy().convert("RGBA"))
            for frame in ImageSequence.Iterator(self.gif)
        ]

        self.frame_index = 0

        self.label_imagen = tk.Label(self.ventana, bg="black", bd=0)
        self.label_imagen.place(
            x=self.ventana.winfo_width() // 2,
            y=self.ventana.winfo_height() // 2,
            anchor="center"
        )

        self.estado = tk.Label(
            self.ventana,
            text="Esperando comando...",
            fg="cyan",
            bg="black",
            font=("Courier", 14)
        )
        self.estado.place(relx=0.5, rely=0.9, anchor="center")

        self.animar()

    def animar(self):
        frame = self.frames[self.frame_index]
        self.label_imagen.config(image=frame)
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.ventana.after(80, self.animar)

    def actualizar_estado(self, texto):
        self.ventana.after(0, lambda: self.estado.config(text=texto))

    def centrar_ventana_en_pantalla(self, ancho, alto):
        self.ventana.update_idletasks()

        pantalla_ancho = self.ventana.winfo_screenwidth()
        pantalla_alto = self.ventana.winfo_screenheight()

        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)

        self.ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    def cambiar_color_texto(self, estado):
        colores = {
            "escuchando": "cyan",
            "Esperando": "lime",
            "pensando": "#b084ff",
            "microfono_activado": "green",
            "microfono_desactivado": "red",
            "hablando": "#00ff88"
        }

        color = colores.get(estado, "cyan")
        self.estado.config(fg=color)

    def mostrar_texto_escuchado(self, texto):
        self.ventana.after(
            0,
            lambda: self.estado.config(text=f"🎧 Escuchado: {texto}")
        )

    def flash_blanco(self, repeticiones=2, duracion=80):
        def flash(contador=0):
            if contador >= repeticiones * 2:
                self.ventana.configure(bg="black")
                return

            color = "white" if contador % 2 == 0 else "black"
            self.ventana.configure(bg=color)
            self.ventana.after(duracion, lambda: flash(contador + 1))

        flash()

    def vibrar(self, intensidad=10, repeticiones=15, velocidad=20):
        x = self.ventana.winfo_x()
        y = self.ventana.winfo_y()

        def mover(i=0):
            if i >= repeticiones:
                self.ventana.geometry(f"+{x}+{y}")
                return

            desplazamiento = intensidad if i % 2 == 0 else -intensidad
            self.ventana.geometry(f"+{x + desplazamiento}+{y}")
            self.ventana.after(velocidad, lambda: mover(i + 1))

        mover()


def efecto_explosion(jarvis_ui):
    jarvis_ui.flash_blanco(repeticiones=4, duracion=60)
    jarvis_ui.vibrar(intensidad=20, repeticiones=25, velocidad=15)


def crear_estado(jarvis_hablando, escuchando, microfono_bloqueado, ultimo_audio, recurso, jarvis_ui):
    return {
        "jarvis_hablando": jarvis_hablando,
        "escuchando": escuchando,
        "microfono_bloqueado": microfono_bloqueado,
        "ultimo_audio": ultimo_audio,
        "recurso": recurso,
        "efecto_explosion": lambda: efecto_explosion(jarvis_ui)
    }