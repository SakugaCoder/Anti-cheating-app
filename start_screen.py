import tkinter as tk
from tkinter import messagebox


class StartScreen (tk.Frame):

    def __init__(self, callback_get_name):
        master = tk.Tk()
        tk.Frame.__init__(self, master)

        self.title = "Bienvenido"
        self.geometry = "400x400"
        self.master = master
        self.master.geometry(self.geometry)
        self.master.title(self.title)
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", self.handle_close)
        self.callback_get_name = callback_get_name

        self.full_name_label = None
        self.full_name_entry = None

        self.btn_width = 150
        self.btn_height = 60
        self.btn_save = None

        self.init_ui()

    def handle_close(self):
        pass

    def exit(self):
        self.master.destroy()

    def handle_submit(self):
        full_name = self.full_name_entry.get()
        if len(full_name) > 10 and len(full_name.split(" ")) >= 3:
            print("All is OK")
            self.callback_get_name(full_name)
        else:
            self.callback_get_name(None)
            messagebox.showerror(
                master=self.master,
                title="Error",
                message="Error. Debe de introducir su nombre completo comenzando con appellido paterno"
            )
        print(full_name)

    def init_ui(self):
        message = """Bienvenido. Está presentando su examen por medio de un entorno seguro. A partir de ahora, cualquier actividad que realice en esta computadora será monitoreada y registrada. Es importante que recuerde que ningún navegador de Internet, programa para correo electrónico, programa de office, paint, editor de fotos o software de redes sociales estará permido durante TODO el tiempo que dura la prueba. No olvide que, aún en caso de terminar su examen con antelación, deberá esperar hasta la hora de término del examen para poder acceder a dichos programas. De otro modo, estaría infringiendo las reglas y esto se registraría en su reporte de actividad. El uso de dispositivos USB también está restringido durante la prueba, favor de tomarlo en cuenta.Se le solicita que por ningún motivo apague su computadora antes de la hora de término del examen.Una vez que se llegue la hora de término del examen, este programa se cerrará automáticamente: generando un archivo comprimido en su escritorio de Windows, el cual contendrá su solución del examen, así como el reporte de su actividad durante el mismo. Este es el archivo que deberá enviar a su profesor para poder ser evaluado.Mucho Éxito en su prueba!"""

        messagebox.showinfo(
            master=self.master,
            title="Bienvenido",
            message=message
        )

        self.full_name_label = tk.Label(self.master, text="Por favor introduce tu nombre:")
        self.full_name_label.place(x=40, y=5)
        full_name_entry_var = tk.StringVar(self.master, value="")

        self.full_name_entry = tk.Entry(
            self.master,
            textvar=full_name_entry_var,
            justify="center",
            state="normal"
        )

        self.full_name_entry .place(
            x=40,
            y=40,
            width=300,
            height=40
        )

        self.full_name_entry.focus_set()

        self.btn_save = tk.Button(
            self.master,
            text="Avanzar",
            font=("Open Sans", 14),
            command=self.handle_submit
        )

        self.btn_save.place(
            x=110,
            y=150,
            width=self.btn_width,
            height=self.btn_height
        )