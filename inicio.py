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

BASE_DIR = str(Path.home()).replace("\\", "/")+"/.anca/"
TEST_DURATION = 30  # Minutes
start_time = None
finish_time = None

test_finished = False
monitor_processes_thread = None
monitor_time_thread = None
monitor_usb_thread = None

log_file = None

CHEATING_FLAG = False
TEST_NOT_FINISHED_ON_TIME_FLAG = False

NORMAL_ACTIVITY = 0
CHEATING_ID = 1
TEST_NOT_FINISHED_ON_TIME_ID = 2
CHEATING_AND_TEST_NOT_FINISHED_ON_TIME = 3

START_TIME = "15:30"
END_TIME = "22:20"

banned_processes_founded = {}

btn_start_test, btn_finish_test, btn_upload_test = None, None, None

full_name_entry = None
user_full_name = ""

ss = None

test_file_path = ""

TEST_STARTED = False

usb_plugged = False

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


def create_directory():
    user_path = str(Path.home()).replace("\\","/")
    try:
        os.listdir(user_path+"/.anca")
        print("Dir exists")

    except Exception as e:
        print(e)
        print("Directorty doesn't exist")
        os.mkdir(f"{str(Path.home())}\\.anca")
        os.mkdir(f"{str(Path.home())}\\.anca\\assets")
        os.mkdir(f"{str(Path.home())}\\.anca\\assets\\files")
        os.mkdir(f"{str(Path.home())}\\.anca\\assets\\log")
        os.mkdir(f"{str(Path.home())}\\.anca\\assets\\result")


def create_result_file(id):
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
    pass


def get_processes():
    processes = []
    for process in psutil.process_iter(["pid", "name", "username"]):
        # (process.info)
        processes.append(process.name())

    return processes


def copy_test(test_path):
    final_path = BASE_DIR.replace("/","\\")+ "\\assets\\files\\"
    test_path = test_path.replace("/", "\\")
    shutil.copy(test_path, final_path)


# def get_banned_processes():
#     banned_processes_df = pd.read_csv(BANNED_PROCESS_FILE)
#     banned_processes = {}
#     for process in banned_processes_df.iterrows():
#         print(process)
#         banned_processes[process[1]["Banned process"]] = process[1]["Alias"]
#     return banned_processes


def monitor_processes(first_scan=False):
    global test_finished, CHEATING_FLAG, banned_processes_founded, log_file
    while not test_finished:
        print(banned_processes)

        # print("Scanning")
        actual_processes = get_processes()
        for banned_process in banned_processes:
            alias = banned_processes[banned_process]
            if banned_process  in actual_processes:
                process_data = {
                    "name": banned_process,
                    "alias": alias,
                    "time": datetime.now().isoformat()
                }
                if banned_process not in banned_processes_founded:
                    if not first_scan:
                        messagebox.showerror(
                            title="Se ha abierto un programa no permitido",
                            message="Se reportara esta acción. El programa es: {}".format(alias))
                    banned_processes_founded[banned_process] = process_data
                if not CHEATING_FLAG:
                    CHEATING_FLAG = True
                    # print(f"{banned_process} exist")

                log_file.add_banned_process(process_data)
        log_file.add_activity()
        if first_scan:
            break

        time.sleep(1)


def monitor_time():
    global test_finished, start_time, TEST_NOT_FINISHED_ON_TIME_FLAG
    start_time = datetime.now()
    start_minute = start_time.second
    last_minute = start_minute
    total_test_minutes = 0
    while not test_finished:
        actual_minute = datetime.now().second
        if last_minute != actual_minute:
            last_minute = actual_minute
            total_test_minutes += 1
            #print(f"Total minutes: {total_test_minutes}")

        if total_test_minutes == TEST_DURATION:
            #print("THE TEST HAS FINISHED")
            if not TEST_NOT_FINISHED_ON_TIME_FLAG:
                TEST_NOT_FINISHED_ON_TIME_FLAG = True


def monitor_usb(first_scan=False):
    global test_finished, log_file, usb_plugged
    pythoncom.CoInitialize()
    c = wmi.WMI()
    while not test_finished:
        for drive in c.Win32_DiskDrive():
            dc = str(drive.caption).upper()
            print(dc)
            try:
                dc.index("USB")
                print("USB detected")
                if not first_scan:
                    tkinter.messagebox.showerror("USB detectado", "Se reportara esta acción")
                log_file.add_media_connected(drive.caption)
                usb_plugged = True
            except Exception as e:
                try:
                    dc.index("SD")
                    print("SD detected")
                    if not first_scan:
                        tkinter.messagebox.showerror("SD detectado", "Se reportara esta acción")
                    log_file.add_media_connected(drive.caption)
                    usb_plugged = True
                except Exception as e:
                    pass
        if first_scan:
            break


def start_test():
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
        os.startfile("sb.url")
    # subprocess.run(['start', "sb.url"], shell=True)
    # subprocess.run("start sb.url", shell=True)


def upload_test():
    global log_file, test_file_path
    file_name = askopenfilename(
        initialdir="/",
        title="Selecciona el archivo",
        filetypes=( ("Archivos PDF", ".pdf"), ("Archivos word", "docx"), ("Todos los archivos", "*.*") )
    )
    test_file_path = file_name
    log_file.add_test(test_file_path)
    print(file_name)
    if len(test_file_path) > 0:
        copy_test(file_name)
        messagebox.showinfo(title="Operación realizada exitosamente", message="Prueba cargada con exito")


def remove_files():
    time.sleep(1)
    print("Deleting file...")
    shutil.rmtree(f"{str(Path.home())}\\.anca")


def finish_test():
    global monitor_processes_thread, monitor_time_thread, test_finished, window, start_time, finish_time
    global monitor_usb_thread
    global START_TIME, END_TIME
    global test_file_path
    global log_file
    global CHEATING_FLAG

    end_time_hour = int(END_TIME.split(":")[0])
    end_time_minute = int(END_TIME.split(":")[1])
    now = datetime.now()
    actual_hour = now.hour
    actual_minute = now.minute

    # if actual_hour >= end_time_hour and actual_minute >= end_time_minute:
    if len(os.listdir(BASE_DIR+"/assets/files") ) == 0:
        examen_blanco = messagebox.askquestion(title="Examen en blanco",
            message="No se ha detectado ninguna entrega, ¿En verdad desea entregar su examen en blanco?",
        )
        if examen_blanco == "yes":
            test_finished = True
            if monitor_processes_thread is not None:
                monitor_processes_thread.join()
            if monitor_time_thread is not None:
                monitor_time_thread.join()
            if monitor_usb_thread is not None:
                monitor_usb_thread.join()
            window.destroy()

            finish_time = datetime.now().isoformat()
            log_file.add_finish_time(finish_time)



            print(f"Inicio: {start_time}\nTermino: {finish_time}")

            if CHEATING_FLAG and TEST_NOT_FINISHED_ON_TIME_FLAG:
                print("Usuario no termino a tiempo y hizo trampa")
                create_result_file(3)
                log_file.add_no_on_time()

            elif CHEATING_FLAG:
                print("Usuario hizo trampa")
                create_result_file(1)
            elif TEST_NOT_FINISHED_ON_TIME_FLAG:
                print("Usuario no termino a tiempo")
                create_result_file(2)
                log_file.add_no_on_time()
            else:
                print("Usuario termino a tiempo y no hizo trampa")
                create_result_file(0)
            time.sleep(2)
            tar_file_name = BASE_DIR + f"assets/result/{log_file.get_username()}.tar"
            tar_file = tarfile.open(tar_file_name, mode="w")
            tar_file.add(BASE_DIR + "assets/student.db")
            tar_file.add(BASE_DIR + "assets/log/")
            tar_file.add(BASE_DIR + "assets/files/")
            tar_file.close()
            encrypt_file(tar_file_name)

            remove_files()

        #print(examen_blanco)

    else:
        test_finished = True
        if monitor_processes_thread is not None:
            monitor_processes_thread.join()
        if monitor_time_thread is not None:
            monitor_time_thread.join()
        if monitor_usb_thread is not None:
            monitor_usb_thread.join()
        window.destroy()

        finish_time = datetime.now().isoformat()
        log_file.add_finish_time(finish_time)

        time.sleep(2)

        if CHEATING_FLAG and TEST_NOT_FINISHED_ON_TIME_FLAG:
            print("Usuario no termino a tiempo y hizo trampa")
            create_result_file(3)
            log_file.add_no_on_time()
        elif CHEATING_FLAG:
            print("Usuario hizo trampa")
            create_result_file(1)
        elif TEST_NOT_FINISHED_ON_TIME_FLAG:
            print("Usuario no termino a tiempo")
            create_result_file(2)
            log_file.add_no_on_time()
        else:
            print("Usuario termino a tiempo y no hizo trampa")
            create_result_file(0)

        tar_file_name = BASE_DIR+f"assets/result/{log_file.get_username()}.tar"
        tar_file = tarfile.open(tar_file_name, mode="w")
        tar_file.add(BASE_DIR + "assets/student.db")
        tar_file.add(BASE_DIR+"assets/log/")
        tar_file.add(BASE_DIR+"assets/files/")

        tar_file.close()
        encrypt_file(tar_file_name)
        remove_files()
        print(f"Inicio: {start_time}\nTermino: {finish_time}")
    """
    else:
        messagebox.showerror(
            title="Error no se puede cerrar la prueba",
            message="Se debe de cumplir el tiempo para poder cerrar la prueba"
        )
    """


def set_start_time(dt):
    global log_file
    print("Setting start time")
    log_file.add_start_time(dt)
    start_test()


def get_student_data(name, group):
    global log_file, ss
    if name is not None:
        log_file.add_username(name)
        log_file.add_group(group)
        ss.exit()
        print(f"Name: {name}, Group: {group}")


def encrypt_file(file_path):
    global log_file
    buffer_size = 1024 * 64
    password = "secret"
    with open(file_path, "rb") as f_in:
        with open(str(Path.home()).replace("\\", "/")+f"/Desktop/{log_file.get_username()}.aes", "wb") as f_out:
            pyAesCrypt.encryptStream(fIn=f_in, fOut=f_out, passw=password, bufferSize=buffer_size)


def main():
    # Thread setup
    global monitor_processes_thread, monitor_time_thread, monitor_usb_thread, window
    global START_TIME, END_TIME
    global banned_processes_founded
    global btn_start_test, btn_upload_test, btn_finish_test
    global full_name_entry
    global log_file
    global ss

    create_directory()

    monitor_processes_thread = threading.Thread(target=monitor_processes)
    monitor_time_thread = threading.Thread(target=monitor_time)
    monitor_usb_thread = threading.Thread(target=monitor_usb)

    log_file = LogFile()
    monitor_processes(first_scan=True)
    monitor_usb(first_scan=True)

    if len(banned_processes_founded) > 0:
        banned_process = [banned_processes_founded[process]['alias'] for process in banned_processes_founded]
        messagebox.showerror(
            title="No se puede iniciar la prueba",
            message="Cerrar los siguientes programas: {}".format(", ".join(banned_process))
        )
        #window.destroy()

    elif usb_plugged:
        messagebox.showerror(
            title="No se puede iniciar la prueba",
            message="Favor de desconectar cualquier medio de almacenamiento USB/SD"
        )
    else:
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
        ss = StartScreen(get_student_data, set_start_time)
        ss.focus_force()
        ss.mainloop()

        # Configure window

        window = tkinter.Tk()
        window.title("Secure Exam")
        window.geometry("720x400")
        window.resizable(False, False)

        # Configure buttons

        # log_file.add_start_time(datetime.now().isoformat())

        btn_width = 200
        btn_height = 60

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

        window.focus_force()
        window.protocol("WM_DELETE_WINDOW", lambda : None)
        window.mainloop()
    """
    else:
        messagebox.showerror(
            "Error al abrir la prueba","La hora actual no concuerda"\
            " con la hora de la prubea que es de: {} a {}".format(START_TIME, END_TIME)
        )

        #window.destroy()
    """


class StartScreen (tkinter.Frame):

    def __init__(self, callback_get_name, callback_start_test):
        master = tkinter.Tk()
        tkinter.Frame.__init__(self, master)

        self.title = "Bienvenido"
        self.geometry = "400x400"
        self.master = master
        self.master.geometry(self.geometry)
        self.master.title(self.title)
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", self.handle_close)
        self.callback_get_name = callback_get_name
        self.callback_start_test = callback_start_test

        self.full_name_label = None
        self.full_name_entry = None

        self.group_label = None
        self.group_entry = None

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
        group = self.group_entry.get()
        if len(full_name) > 10 and len(full_name.split(" ")) >= 3 and len(group) > 0:
            self.callback_get_name(full_name, group)
        else:
            self.callback_get_name(None, None)
            msg = "Error. Debe de introducir su nombre completo comenzando con appellido paterno"
            if len(group) == 0:
                msg = "Error. Por favor ingresar un grupo"
            messagebox.showerror(
                master=self.master,
                title="Error",
                message=msg
            )

    def init_ui(self):
        message = """Bienvenido. Está presentando su examen por medio de un entorno seguro. A partir de ahora, cualquier actividad que realice en esta computadora será monitoreada y registrada. Es importante que recuerde que ningún navegador de Internet, programa para correo electrónico, programa de office, paint, editor de fotos o software de redes sociales estará permido durante TODO el tiempo que dura la prueba. No olvide que, aún en caso de terminar su examen con antelación, deberá esperar hasta la hora de término del examen para poder acceder a dichos programas. De otro modo, estaría infringiendo las reglas y esto se registraría en su reporte de actividad. El uso de dispositivos USB también está restringido durante la prueba, favor de tomarlo en cuenta.Se le solicita que por ningún motivo apague su computadora antes de la hora de término del examen.Una vez que se llegue la hora de término del examen, este programa se cerrará automáticamente: generando un archivo comprimido en su escritorio de Windows, el cual contendrá su solución del examen, así como el reporte de su actividad durante el mismo. Este es el archivo que deberá enviar a su profesor para poder ser evaluado.Mucho Éxito en su prueba!"""

        question = messagebox.showinfo(
            master=self.master,
            title="Bienvenido",
            message=message
        )

        self.callback_start_test(datetime.now().isoformat())


        # Name field
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

        # Group field
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

if __name__ == "__main__":
    main()


