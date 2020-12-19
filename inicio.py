import threading
import time
import os
import tkinter
import tarfile
import pyAesCrypt
import shutil
import psutil
import wmi
import pythoncom

from tkinter.filedialog import askopenfilename
from datetime import datetime
from tkinter import messagebox
from log import LogFile

from pathlib import Path

# Variables globales

# Declara directorio base para el funcionamiento del programa
BASE_DIR = str(Path.home()).replace("\\", "/")+"/.anca/"
TEST_DURATION = 30  # Duración de la prueba en minutos
start_time = None   # Hora de inicio de la prueba
finish_time = None  # Hora de termino de la prueba

test_finished = False   # Bandera para identificar el temrino de la prueba
monitor_processes_thread = None  # Variable para almacenar el hilo del proceso para monitorear procesos
monitor_time_thread = None  # Variable para almacenar el hilo del proceso para monitoriar el tiempo de la prueba
monitor_usb_thread = None   # Variable para almacenar el hilo del proceso para monitoriar la conexión de unidades USB

log_file = None # Variable para almacenar el archivo de registro de actividad

# Banderas para establecer trampa en prueba y prueba no terminada a tiempo respectivamente
CHEATING_FLAG = False
TEST_NOT_FINISHED_ON_TIME_FLAG = False


# NORMAL_ACTIVITY = 0
# CHEATING_ID = 1
# TEST_NOT_FINISHED_ON_TIME_ID = 2
# CHEATING_AND_TEST_NOT_FINISHED_ON_TIME = 3

# Variables para controlar el tiempo de inicio y termino de la prueba
START_TIME = "15:30"
END_TIME = "22:20"

# Variable para almacenar los procesos prohibidos encontrados
banned_processes_founded = {}

# Variables para almacenar los botones de la interfaz principal
btn_start_test, btn_finish_test, btn_upload_test = None, None, None

# Varaibales para almacenar el nombre del usuario
full_name_entry = None
user_full_name = ""

# Alamacena un objeto de la clase Start Screen
ss = None

# Almacena la ruta del archivo entregable para la prueba (en caso de existir)
test_file_path = ""


# Bandera para establecer que la prueba inicio
TEST_STARTED = False

# Bandera para establecer que se ha conectado un dispositivo USB
usb_plugged = False

# Diccionario para los procesos prohibidos
banned_processes = {
    # "chrome.exe": "Chrome",
    "firefox.exe": "Firefox",
    "opera.exe": "Opera",
    "msedge.exe": "Microsoft Edge",
    "WhatsApp.exe": "Whatsapp",
    "iexplore.exe": "Internet Explorer",
    "Taskmgr.exe": "Administrador de tareas",
    "notepad.exe": "Bloc de notas",
    # "EXCEL.EXE": "Excel",
    # "WINWORD.EXE": "Word",
    "POWERPNT.EXE": "PowerPoint",
    "thunderbird.exe": "Thunderbird",
    # "HxTsr.exe": "Correo de microsoft",
    "FacebookMessenger.exe": "Facebook Messenger"
}

# Función para crear los directorios necesarios para arrancar el programa
def create_directory():
    # Directorio del usuario actual
    user_path = str(Path.home()).replace("\\", "/")
    # Si el directorio no existe se crea
    try:
        os.listdir(user_path+"/.anca")
        print("Dir exists")

    except Exception as e:
        print(e)
        print("Directorty doesn't exist")

        # Crea carpetas necesarias para el funcionamiento del programa
        os.mkdir(f"{str(Path.home())}\\.anca")
        os.mkdir(f"{str(Path.home())}\\.anca\\assets")
        os.mkdir(f"{str(Path.home())}\\.anca\\assets\\files")
        os.mkdir(f"{str(Path.home())}\\.anca\\assets\\log")
        os.mkdir(f"{str(Path.home())}\\.anca\\assets\\result")


# def create_result_file(id):
    # global finish_time, banned_processes_founded
    # global user_full_name
    # ts = datetime.timestamp(finish_time)
    # filename = f"0{id}_{ts}"
    # file = open(RESULT_DIRECTORY+filename, "w+")
    # file.write(f"n: {user_full_name}\n")
    # file.write(f"s:{start_time}\nf:{finish_time}\n")
    # file.write("Process baned founded:\n")
    # for process in banned_processes_founded:
    #     time = banned_processes_founded[process]['time']
    #     alias = banned_processes_founded[process]['alias']
    #     file.write(f"Process: {process}, Alias: {alias}, Time: {time}\n")
    # # file.write(f"Late: {TEST_NOT_FINISHED_ON_TIME_FLAG}")
    # file.close()
    # print("Bye...")
    # pass

# Función para obtener los procesos que estan en ejecución
def get_processes():
    processes = [process.name() for process in psutil.process_iter(['name'])]
    return processes

# Función para copiar el archivo seleccionado como entregable al directorio base del programa
def copy_test(test_path):
    # Define la ruta del archivo final
    final_path = BASE_DIR.replace("/", "\\") + "\\assets\\files\\"
    # Define ruta del archivo seleccionado
    test_path = test_path.replace("/", "\\")
    # Copia archivo
    shutil.copy(test_path, final_path)

# Función para monitoriar procesos. Si se definie como primer escaneo, el proceso solo se realiza una vez
# y termina su ejecución
def monitor_processes(first_scan=False):
    # Define variables globales
    global test_finished, CHEATING_FLAG, banned_processes_founded, log_file

    # Se ejecuta mientras que no se precione el botón de finalizar prueba
    while not test_finished:
        # print(banned_processes)
        # print("Scanning")
        # Obtiene procesos actuales
        actual_processes = get_processes()
        # Itera sobre los procesos prohibidos y verifica que no se encuentre en los procesos actuales
        for banned_process in banned_processes:
            # Obtiene nommbre del proceso baneado
            alias = banned_processes[banned_process]

            # Verifica que el que el proceso prohibido no se encuentre en los procesos actuales
            if banned_process in actual_processes:
                # Guarda datos del proceso
                process_data = {
                    "name": banned_process,
                    "alias": alias,
                    "time": datetime.now().isoformat()
                }

                # Si el proceso no existe en los procesos prohibidos registrados se registra la actividad
                if banned_process not in banned_processes_founded:
                    # Si es el primer escaneo muestra mensaje
                    if not first_scan:
                        messagebox.showerror(
                            title="Se ha abierto un programa no permitido",
                            message="Se reportara esta acción. El programa es: {}".format(alias))
                    # Guarda proceso encontrado
                    banned_processes_founded[banned_process] = process_data
                # Si aun no se ha definido la bandera de proceso encontrado se cambia a verdadero
                if not CHEATING_FLAG:
                    CHEATING_FLAG = True
                    # print(f"{banned_process} exist")
                # Añade proceso prohibido a archivo de log
                log_file.add_banned_process(process_data)
        # Añade actividad a archivo de log
        log_file.add_activity()

        # Si es el primer escaneo se termina el bucle
        if first_scan:
            break

        # Retardo de 1s
        time.sleep(1)

# Función para monitorear el tiempo de la prueba
def monitor_time():
    # Variables globales
    global test_finished, start_time, TEST_NOT_FINISHED_ON_TIME_FLAG
    # Inicializa variables para control de timepo
    start_time = datetime.now()
    start_minute = start_time.second
    last_minute = start_minute
    total_test_minutes = 0

    # Mientras la prueba no termine se se ejecuta el proceso
    while not test_finished:
        # obtiene minutos actuales
        actual_minute = datetime.now().second # Al final cambiara a minutos no segundos

        # Si es diferente a los minutos anteriores se incrementa la variable de minutos de la prueba transcurridos
        if last_minute != actual_minute:
            last_minute = actual_minute
            total_test_minutes += 1
            #print(f"Total minutes: {total_test_minutes}")

        # Si los minutos transcurridos superan los minutos permitidos de la prueba se establece la bandera
        # de no termino a tiempo como verdadera
        if total_test_minutes > TEST_DURATION:
            #print("THE TEST HAS FINISHED")
            if not TEST_NOT_FINISHED_ON_TIME_FLAG:
                TEST_NOT_FINISHED_ON_TIME_FLAG = True


# Función para monitorear la conexión de dispositivos USB/SD
def monitor_usb(first_scan=False):
    # Variables globales
    global test_finished, log_file, usb_plugged
    # Función requerida para correr proceso en segundo plano
    pythoncom.CoInitialize()
    # Variable para guardar un objeto de Windows Management Instrumentation (WMI)
    c = wmi.WMI()

    # Mientras no termine la prueba se se ejecuta el proceso
    while not test_finished:
        # Itera sobre unidades de disco conectadas en el ordenador
        for drive in c.Win32_DiskDrive():
            # Guarda etiqueta de dispositio en letra mayuscula
            dc = str(drive.caption).upper()
            print(dc)
            # Trata de encontrar si es un dispositivo USB
            try:
                dc.index("USB")
                print("USB detected")
                # Si no es el primer escaneo se envia mensaje y se agrega al archivo log la actividad
                if not first_scan:
                    tkinter.messagebox.showerror("USB detectado", "Se reportara esta acción")
                    log_file.add_media_connected(drive.caption)
                # Se define como verdadera la bandera para detectar dispositivos USB conectados
                usb_plugged = True
            except Exception as e:
                # Trata de encontrar si es un dispositivo SD
                try:
                    dc.index("SD")
                    print("SD detected")

                    # Si no es el primer escaneo se envia mensaje y se agrega al archivo log la actividad
                    if not first_scan:
                        tkinter.messagebox.showerror("SD detectado", "Se reportara esta acción")
                        log_file.add_media_connected(drive.caption)

                    # Se define como verdadera la bandera para detectar dispositivos SD conectados
                    usb_plugged = True
                except Exception as e:
                    pass

        # Si es el primer escaneo se termina el bucle
        if first_scan:
            break


# Función para inicializar la prueba en linea
def start_test():
    os.startfile("sb.url")
    """
    # Variables globales
    global monitor_processes_thread, monitor_time_thread, monitor_usb_thread
    global btn_start_test, btn_upload_test, btn_finish_test
    global user_full_name
    global TEST_STARTED
    
    
    if not TEST_STARTED:
        monitor_time_thread.start()
        monitor_processes_thread.start()
        monitor_usb_thread.start()
        TEST_STARTED = True
    else:
    """

# Función para cargar arhcivo adjunto de la prueba
def upload_test():
    # Variables globales
    global log_file, test_file_path

    # Abre cuadro de dialogo y almacena el archivo seleccionado en una variable
    file_name = askopenfilename(
        initialdir="/",
        title="Selecciona el archivo",
        filetypes=(("Archivos PDF", ".pdf"), ("Archivos word", "docx"), ("Todos los archivos", "*.*"))
    )
    test_file_path = file_name

    # Agrega archivo adjunto al log
    log_file.add_test(test_file_path)
    print(file_name)

    # Si selecciono un archivo correcto se procede a copiar al directorio del programa
    if len(test_file_path) > 0:
        # Llama a función para copiar archivo
        copy_test(file_name)
        # Mensaje de exito al cargar prueba
        messagebox.showinfo(title="Operación realizada exitosamente", message="Prueba cargada con exito")

# Función para remover archivos de programa
def remove_files():
    time.sleep(1)
    print("Deleting file...")
    shutil.rmtree(f"{str(Path.home())}\\.anca")

# Función para terminar prueba
def finish_test():
    # Variables globales
    global monitor_processes_thread, monitor_time_thread, test_finished, window, start_time, finish_time
    global monitor_usb_thread
    global START_TIME, END_TIME
    global test_file_path
    global log_file
    global CHEATING_FLAG

    # Obtiene minuto y hora de termino de la prueba
    end_time_hour = int(END_TIME.split(":")[0])
    end_time_minute = int(END_TIME.split(":")[1])
    # Obtiene hora actual
    now = datetime.now()
    actual_hour = now.hour
    actual_minute = now.minute

    # if actual_hour >= end_time_hour and actual_minute >= end_time_minute:
    # Si no se selecciono ningun archivo se pregunta si se desea continuar
    if len(os.listdir(BASE_DIR+"/assets/files") ) == 0:
        examen_blanco = messagebox.askquestion(title="Examen en blanco",
            message="No se ha detectado ninguna entrega, ¿En verdad desea entregar su examen en blanco?",
        )

        # Si seleciono que si finaliza la prueba
        if examen_blanco == "yes":
            test_finished = True
            # Detiene hilos de los procesos de monitoreo
            if monitor_processes_thread is not None:
                monitor_processes_thread.join()
            if monitor_time_thread is not None:
                monitor_time_thread.join()
            if monitor_usb_thread is not None:
                monitor_usb_thread.join()
            window.destroy()

            # Añade hora de termino al archivo log
            finish_time = datetime.now().isoformat()
            log_file.add_finish_time(finish_time)



            print(f"Inicio: {start_time}\nTermino: {finish_time}")

            # Si no termino a tiempo, añade evento al archivo log
            if CHEATING_FLAG and TEST_NOT_FINISHED_ON_TIME_FLAG:
                print("Usuario no termino a tiempo y hizo trampa")
                # create_result_file(3)
                log_file.add_no_on_time()

            elif CHEATING_FLAG:
                print("Usuario hizo trampa")
                # create_result_file(1)
            # Si no termino a tiempo, añade evento al archivo log
            elif TEST_NOT_FINISHED_ON_TIME_FLAG:
                print("Usuario no termino a tiempo")
                # create_result_file(2)
                log_file.add_no_on_time()
            else:
                print("Usuario termino a tiempo y no hizo trampa")
                #create_result_file(0)

            time.sleep(2)
            # Añade archivos de programa a un solo archivo tar
            tar_file_name = BASE_DIR + f"assets/result/{log_file.get_username()}.tar"
            tar_file = tarfile.open(tar_file_name, mode="w")
            tar_file.add(BASE_DIR + "assets/student.db")
            tar_file.add(BASE_DIR + "assets/log/")
            tar_file.add(BASE_DIR + "assets/files/")
            tar_file.close()

            # Encripta archivo compreso
            encrypt_file(tar_file_name)

            # Elimina archivos de programa
            remove_files()

        #print(examen_blanco)

    else:
        test_finished = True
        # Detiene hilos de los procesos de monitoreo
        if monitor_processes_thread is not None:
            monitor_processes_thread.join()
        if monitor_time_thread is not None:
            monitor_time_thread.join()
        if monitor_usb_thread is not None:
            monitor_usb_thread.join()
        window.destroy()

        # Añade hora de termino al archivo log
        finish_time = datetime.now().isoformat()
        log_file.add_finish_time(finish_time)

        time.sleep(2)

        # Si no termino a tiempo, añade evento al archivo log
        if CHEATING_FLAG and TEST_NOT_FINISHED_ON_TIME_FLAG:
            print("Usuario no termino a tiempo y hizo trampa")
            # create_result_file(3)
            log_file.add_no_on_time()
        elif CHEATING_FLAG:
            print("Usuario hizo trampa")
            # create_result_file(1)
        # Si no termino a tiempo, añade evento al archivo log
        elif TEST_NOT_FINISHED_ON_TIME_FLAG:
            print("Usuario no termino a tiempo")
            # create_result_file(2)
            log_file.add_no_on_time()
        else:
            print("Usuario termino a tiempo y no hizo trampa")
            # create_result_file(0)

        # Añade archivos de programa a un solo archivo tar
        tar_file_name = BASE_DIR+f"assets/result/{log_file.get_username()}.tar"
        tar_file = tarfile.open(tar_file_name, mode="w")
        tar_file.add(BASE_DIR + "assets/student.db")
        tar_file.add(BASE_DIR+"assets/log/")
        tar_file.add(BASE_DIR+"assets/files/")
        tar_file.close()

        # Encripta archivo compreso
        encrypt_file(tar_file_name)

        # Remueve archivos de programa
        remove_files()
        print(f"Inicio: {start_time}\nTermino: {finish_time}")
    """
    else:
        messagebox.showerror(
            title="Error no se puede cerrar la prueba",
            message="Se debe de cumplir el tiempo para poder cerrar la prueba"
        )
    """

# Función para establecer la hora en que el usuario inicio la prueba
def set_start_time(dt):
    global log_file
    print("Setting start time")
    # Agrega hora de inicio al archivo log
    log_file.add_start_time(dt)
    # Inicia la prueba
    start_test()


# Función utilizada para guardar el grupo y nombre del estudiante
def get_student_data(name, group):
    # Variables globales
    global log_file, ss

    # Si escribio un nombre correcto se procede a guardar los datos
    if name is not None:
        # Guarda nombre y grupo en el archivo log
        log_file.add_username(name)
        log_file.add_group(group)
        # Cierra ventana de inicio
        ss.exit()
        print(f"Name: {name}, Group: {group}")

# Función para encriptar el archivo tar
def encrypt_file(file_path):
    # Variable global
    global log_file
    # Tamaño del buffer
    buffer_size = 1024 * 64
    # Password para encriptar el archivo
    password = "secret"
    # Abre archivo tar
    with open(file_path, "rb") as f_in:
        # Crea/sobreescribe archivo aes
        with open(str(Path.home()).replace("\\", "/")+f"/Desktop/{log_file.get_username()}.aes", "wb") as f_out:
            # Encripta y genera archivo final
            pyAesCrypt.encryptStream(fIn=f_in, fOut=f_out, passw=password, bufferSize=buffer_size)


# Función principal
def main():
    # Variables globales
    global monitor_processes_thread, monitor_time_thread, monitor_usb_thread, window
    global START_TIME, END_TIME
    global banned_processes_founded
    global btn_start_test, btn_upload_test, btn_finish_test
    global full_name_entry
    global log_file
    global ss

    # Crea directorios del programa / si es que no existen
    create_directory()

    # Inicializa variables para almacenar hilos
    monitor_processes_thread = threading.Thread(target=monitor_processes)
    monitor_time_thread = threading.Thread(target=monitor_time)
    monitor_usb_thread = threading.Thread(target=monitor_usb)

    # Inicializa archivo de log
    log_file = LogFile()

    # Realiza escaneo de procesos y USB por primera vez
    monitor_processes(first_scan=True)
    monitor_usb(first_scan=True)

    # Si se encontraron procesos prohibidos se muestra mensaje con cada uno de ellos y finaliza ejecución
    if len(banned_processes_founded) > 0:
        banned_process = [banned_processes_founded[process]['alias'] for process in banned_processes_founded]
        messagebox.showerror(
            title="No se puede iniciar la prueba",
            message="Cerrar los siguientes programas: {}".format(", ".join(banned_process))
        )
        #window.destroy()

    # Si se encontro un dispositivo USB conectado muestra mensaje de alerta y finaliza ejecución
    elif usb_plugged:
        messagebox.showerror(
            title="No se puede iniciar la prueba",
            message="Favor de desconectar cualquier medio de almacenamiento USB/SD"
        )

    # Si no se encontro nada sospechoso se procede con la ejecución normal del programa
    else:
        # Inicializa variables de tiempo
        end_time_hour = int(END_TIME.split(":")[0])
        end_time_minute = int(END_TIME.split(":")[1])

        start_time_hour = int(START_TIME.split(":")[0])
        start_time_minute = int(START_TIME.split(":")[1])
        now = datetime.now()

        actual_hour = now.hour
        actual_minute = now.minute

        print(f"\nStart time: {start_time_hour}:{start_time_minute}")
        print(f"End time: {end_time_hour}:{end_time_minute}")
        print(f"Actual time: {actual_hour}:{actual_minute}")

        """
        if (start_time_hour == actual_hour and start_time_minute <= actual_minute and start_time_hour != end_time_hour)\
            or\
            (end_time_hour == actual_hour and end_time_minute >= actual_minute and start_time_hour != end_time_hour)\
            or\
            (start_time_hour == end_time_hour and start_time_minute <= actual_minute < end_time_minute)\
            or\
            (start_time_hour < actual_hour < end_time_hour):

        """

        # Crea pantalla de inicio
        ss = StartScreen(get_student_data, set_start_time)
        ss.focus_force()
        ss.mainloop()

        # Configura ventana principal del programa
        window = tkinter.Tk()
        window.title("Secure Exam")
        window.geometry("720x400")
        window.resizable(False, False)


        # log_file.add_start_time(datetime.now().isoformat())



        # Establece dimensiones de botones
        btn_width = 200
        btn_height = 60

        # Crea botones principales inicio de prueba en linea, entregar archivo adjunto y finalizar
        # prueba respectivamente

        btn_start_test = tkinter.Button(
            window,
            text="Iniciar prueba en linea",
            font=("Open Sans", 10),
            command=start_test
        )

        btn_start_test.place(
            x=20,
            y=150,
            width=btn_width,
            height=btn_height
        )

        btn_upload_test = tkinter.Button(
            window,
            text="Entregar archivo adjunto",
            font=("Open Sans", 10),
            command=upload_test,
            # state="disabled"
        )

        btn_upload_test.place(
            x=250,
            y=150,
            width=btn_width,
            height=btn_height
        )

        btn_finish_test = tkinter.Button(
            window,
            text="Finalizar Prueba",
            font=("Open Sans", 10),
            command=finish_test,
        )

        btn_finish_test.place(
            x=500,
            y=150,
            width=btn_width,
            height=btn_height
        )

        # Forza foco en ventana actual
        window.focus_force()

        # Si se presiona el botón de cerrar ventana no realiza nada
        window.protocol("WM_DELETE_WINDOW", lambda : None)

        # Inicia ventana principal
        window.mainloop()
    """
    else:
        messagebox.showerror(
            "Error al abrir la prueba","La hora actual no concuerda"\
            " con la hora de la prubea que es de: {} a {}".format(START_TIME, END_TIME)
        )

        #window.destroy()
    """

# Clase para la creación de la ventana de inicio
class StartScreen (tkinter.Frame):

    # Inicializa la ventana de inicio
    def __init__(self, callback_get_name, callback_start_test):
        master = tkinter.Tk()
        tkinter.Frame.__init__(self, master)

        # Configura principales parametros de la ventana de inicio
        self.title = "Bienvenido"
        self.geometry = "400x400"
        self.master = master
        self.master.geometry(self.geometry)
        self.master.title(self.title)
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", self.handle_close)
        self.callback_get_name = callback_get_name
        self.callback_start_test = callback_start_test

        # Define variables principales de la ventana de inicio
        self.full_name_label = None
        self.full_name_entry = None

        self.group_label = None
        self.group_entry = None

        self.btn_width = 150
        self.btn_height = 60
        self.btn_save = None

        # Inicializa la interfaz
        self.init_ui()

    # Función para manejar el cerrado de la ventana (no realiza nada).
    def handle_close(self):
        pass

    # Función para salir de la ventana
    def exit(self):
        self.master.destroy()

    # Función para manejar la presión del botón para guardar datos
    def handle_submit(self):
        # Obtiene nombre y grupo de los campos de la interfaz
        full_name = self.full_name_entry.get()
        group = self.group_entry.get()

        # Realiza validación para cada campo
        if len(full_name) > 10 and len(full_name.split(" ")) >= 3 and len(group) > 0:
            # Si son correctos los campos se procede a guardar los datos
            self.callback_get_name(full_name, group)
        else:
            # Si no son validos los campos muestra mensaje de error pertinente
            self.callback_get_name(None, None)
            msg = "Error. Debe de introducir su nombre completo comenzando con appellido paterno"
            if len(group) == 0:
                msg = "Error. Por favor ingresar un grupo"
            messagebox.showerror(
                master=self.master,
                title="Error",
                message=msg
            )

    # Función para inicializar los componentes en la pantalla de inicio
    def init_ui(self):
        # Muestra mensaje de bienbenida
        message = """Bienvenido. Está presentando su examen por medio de un entorno seguro. A partir de ahora, cualquier actividad que realice en esta computadora será monitoreada y registrada. Es importante que recuerde que ningún navegador de Internet, programa para correo electrónico, programa de office, paint, editor de fotos o software de redes sociales estará permido durante TODO el tiempo que dura la prueba. No olvide que, aún en caso de terminar su examen con antelación, deberá esperar hasta la hora de término del examen para poder acceder a dichos programas. De otro modo, estaría infringiendo las reglas y esto se registraría en su reporte de actividad. El uso de dispositivos USB también está restringido durante la prueba, favor de tomarlo en cuenta.Se le solicita que por ningún motivo apague su computadora antes de la hora de término del examen.Una vez que se llegue la hora de término del examen, este programa se cerrará automáticamente: generando un archivo comprimido en su escritorio de Windows, el cual contendrá su solución del examen, así como el reporte de su actividad durante el mismo. Este es el archivo que deberá enviar a su profesor para poder ser evaluado.Mucho Éxito en su prueba!"""

        question = messagebox.showinfo(
            master=self.master,
            title="Bienvenido",
            message=message
        )

        # Llama función para inicializar prueba en el momento que el usuario presione ok o cierre el mensaje
        # de bienvenida
        self.callback_start_test(datetime.now().isoformat())

        # Define la entrada y el labelpara el nombre
        self.full_name_label = tkinter.Label(self.master, text="Por favor introduce tu nombre:")
        self.full_name_label.place(x=40, y=5)
        full_name_entry_var = tkinter.StringVar(self.master, value="")

        self.full_name_entry = tkinter.Entry(
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

        # Define la entrada y label para el grupo
        self.group_label = tkinter.Label(self.master, text="Grupo:")
        self.group_label.place(x=40, y=150)
        group_entry_var = tkinter.StringVar(self.master, value="")

        self.group_entry = tkinter.Entry(
            self.master,
            textvar=group_entry_var,
            justify="center",
            state="normal"
        )

        self.group_entry.place(
            x=40,
            y=185,
            width=300,
            height=40
        )

        self.btn_save = tkinter.Button(
            self.master,
            text="Avanzar",
            font=("Open Sans", 14),
            command=self.handle_submit
        )

        self.btn_save.place(
            x=110,
            y=240,
            width=self.btn_width,
            height=self.btn_height
        )


# Valida que solo se pueda inicializar desde el programa principal
if __name__ == "__main__":
    main()
