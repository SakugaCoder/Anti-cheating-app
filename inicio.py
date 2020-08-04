import threading
import time
import os
import tkinter
import tarfile
import pyAesCrypt
import shutil
import subprocess

from tkinter.filedialog import askopenfilename
from datetime import datetime
from tkinter import messagebox
from log import LogFile
from start_screen import StartScreen
from pathlib import Path

BASE_DIR = str(Path.home()).replace("\\", "/")+"/.anca/"
TEST_DURATION = 30  # Minutes
start_time = None
finish_time = None

test_finished = False
monitor_processes_thread = None
monitor_time_thread = None

log_file = None

CHEATING_FLAG = False
TEST_NOT_FINISHED_ON_TIME_FLAG = False

NORMAL_ACTIVITY = 0
CHEATING_ID = 1
TEST_NOT_FINISHED_ON_TIME_ID = 2
CHEATING_AND_TEST_NOT_FINISHED_ON_TIME = 3

START_TIME = "10:30"
END_TIME = "13:30"

banned_processes_founded = {}

btn_start_test, btn_finish_test, btn_upload_test = None, None, None

full_name_entry = None
user_full_name = ""

ss = None

test_file_path = ""

TEST_STARTED = False

banned_processes = {
    #"chrome.exe": "Chrome",
    "firefox.exe": "Firefox",
    "opera.exe": "Opera",
    "msedge.exe": "Microsoft Edge",
    "WhatsApp.exe": "Whatsapp",
    "iexplore.exe": "Internet Explorer",
    "Taskmgr.exe": "Administrador de tareas",
    "notepad.exe": "Bloc de notas",
    #"EXCEL.EXE": "Excel",
    "WINWORD.EXE": "Word",
    "POWERPNT.EXE": "PowerPoint",
    "thunderbird.exe": "Thunderbird",
    "HxTsr.exe": "Correo de microsoft",
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


def process_exists(process):

    cmd = f"tasklist | findstr {process} > tmp"
    print(cmd)
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #output = ps.communicate()[0]
    time.sleep(1)
    file_size = os.path.getsize(f"{os.getcwd()}\\tmp")
    #os.remove(f"{os.getcwd()}\\tmp")
    print(file_size)
    #print(output)

    if file_size > 0:
        print("Process exists")
        return True
    else:
        print("process doesn't exists")
        return False


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
    if not first_scan:
        print("Escaneando en segundo plano")
    while not test_finished:
        print(banned_processes)

        print("Scanning")
        for banned_process in banned_processes:
            alias = banned_processes[banned_process]
            if process_exists(banned_process):
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
                    print(f"{banned_process} exist")

                log_file.add_banned_process(process_data)
            time.sleep(0.5)
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


def start_test():
    global monitor_processes_thread, monitor_time_thread
    global btn_start_test, btn_upload_test, btn_finish_test
    global user_full_name
    global TEST_STARTED

    if not TEST_STARTED:
        btn_upload_test.config(state="normal")
        btn_start_test.config(state="normal")
        btn_finish_test.config(state="normal")

        pythoncom.CoInitialize()
        monitor_time_thread.start()
        monitor_processes_thread.start()
        TEST_STARTED = True

    os.system("start sb.url")


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


def finish_test():
    global monitor_processes_thread, monitor_time_thread, test_finished, window, start_time, finish_time
    global START_TIME, END_TIME
    global test_file_path
    global log_file
    global CHEATING_FLAG

    end_time_hour = int(END_TIME.split(":")[0])
    end_time_minute = int(END_TIME.split(":")[1])
    now = datetime.now()
    actual_hour = now.hour
    actual_minute = now.minute

    if actual_hour >= end_time_hour and actual_minute >= end_time_minute:
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
                window.destroy()

                finish_time = datetime.now().isoformat()
                log_file.add_finish_time(finish_time)

                time.sleep(2)
                tar_file_name = BASE_DIR + "assets/result/output.tar"
                tar_file = tarfile.open(tar_file_name, mode="w")
                tar_file.add(BASE_DIR + "assets/log/")
                tar_file.add(BASE_DIR + "assets/files/")
                tar_file.close()
                encrypt_file(BASE_DIR + "assets/result/output.tar")

                print(f"Inicio: {start_time}\nTermino: {finish_time}")

                if CHEATING_FLAG and TEST_NOT_FINISHED_ON_TIME_FLAG:
                    print("Usuario no termino a tiempo y hizo trampa")
                    create_result_file(3)
                elif CHEATING_FLAG:
                    print("Usuario hizo trampa")
                    create_result_file(1)
                elif TEST_NOT_FINISHED_ON_TIME_FLAG:
                    print("Usuario no termino a tiempo")
                    create_result_file(2)
                else:
                    print("Usuario termino a tiempo y no hizo trampa")
                    create_result_file(0)

            #print(examen_blanco)

        else:
            test_finished = True
            if monitor_processes_thread is not None:
                monitor_processes_thread.join()
            if monitor_time_thread is not None:
                monitor_time_thread.join()
            window.destroy()

            finish_time = datetime.now().isoformat()
            log_file.add_finish_time(finish_time)

            time.sleep(2)
            tar_file_name = BASE_DIR+"assets/result/output.tar"
            tar_file = tarfile.open(tar_file_name, mode="w")
            tar_file.add(BASE_DIR+"assets/log/")
            tar_file.add(BASE_DIR+"assets/files/")
            tar_file.close()
            encrypt_file(BASE_DIR+"assets/result/output.tar")



            print(f"Inicio: {start_time}\nTermino: {finish_time}")


            if CHEATING_FLAG and TEST_NOT_FINISHED_ON_TIME_FLAG:
                print("Usuario no termino a tiempo y hizo trampa")
                create_result_file(3)
            elif CHEATING_FLAG:
                print("Usuario hizo trampa")
                create_result_file(1)
            elif TEST_NOT_FINISHED_ON_TIME_FLAG:
                print("Usuario no termino a tiempo")
                create_result_file(2)
            else:
                print("Usuario termino a tiempo y no hizo trampa")
                create_result_file(0)
    else:
        messagebox.showerror(
            title="Error no se puede cerrar la prueba",
            message="Se debe de cumplir el tiempo para poder cerrar la prueba"
        )


def get_name(name):
    global log_file, ss
    if name is not None:
        log_file.add_username(name)
        ss.exit()
        print(name)


def encrypt_file(file_path):
    buffer_size = 1024 * 64
    password = "secret"
    with open(file_path, "rb") as f_in:
        with open(str(Path.home()).replace("\\","/")+"/Desktop/encrypt.aes", "wb") as f_out:
            pyAesCrypt.encryptStream(fIn=f_in, fOut=f_out, passw=password, bufferSize=buffer_size)


def main():
    # Thread setup
    global monitor_processes_thread, monitor_time_thread, window
    global START_TIME, END_TIME
    global banned_processes_founded
    global btn_start_test, btn_upload_test, btn_finish_test
    global full_name_entry
    global log_file
    global ss

    create_directory()

    monitor_processes_thread = threading.Thread(target=monitor_processes)
    monitor_time_thread = threading.Thread(target=monitor_time)

    log_file = LogFile()
    monitor_processes(first_scan=True)
    if len(banned_processes_founded) > 0:
        banned_process = [banned_processes_founded[process]['alias'] for process in banned_processes_founded]
        messagebox.showerror(
            title="No se puede iniciar la prueba",
            message="Cerrar los siguientes programas: {}".format(", ".join(banned_process))
        )
        #window.destroy()

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

        if (start_time_hour == actual_hour and start_time_minute <= actual_minute and start_time_hour != end_time_hour)\
            or\
            (end_time_hour == actual_hour and end_time_minute >= actual_minute and start_time_hour != end_time_hour)\
            or\
            (start_time_hour == end_time_hour and start_time_minute <= actual_minute < end_time_minute)\
            or\
            (start_time_hour < actual_hour < end_time_hour):

            ss = StartScreen(get_name)
            ss.focus_force()
            ss.mainloop()

            # Configure window

            window = tkinter.Tk()
            window.title("Secure Exam")
            window.geometry("600x400")
            window.resizable(False, False)

            # Configure buttons

            log_file.add_start_time(datetime.now().isoformat())

            btn_width = 150
            btn_height = 60

            btn_start_test = tkinter.Button(
                window,
                text="Iniciar Prueba",
                font=("Open Sans", 14),
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
                text="Subir Prueba",
                font=("Open Sans", 14),
                command=upload_test,
                state="disabled"
            )

            btn_upload_test.place(
                x=200,
                y=150,
                width=btn_width,
                height=btn_height
            )

            btn_finish_test = tkinter.Button(
                window,
                text="Finalizar Prueba",
                font=("Open Sans", 14),
                command=finish_test,
                state="disabled"
            )

            btn_finish_test.place(
                x=400,
                y=150,
                width=btn_width,
                height=btn_height
            )

            window.focus_force()
            window.protocol("WM_DELETE_WINDOW", lambda : None)
            window.mainloop()
        else:
            messagebox.showerror(
                "Error al abrir la prueba","La hora actual no concuerda"\
                " con la hora de la prubea que es de: {} a {}".format(START_TIME, END_TIME)
            )

            #window.destroy()

main()
