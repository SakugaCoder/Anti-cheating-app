import threading
import pandas as pd
from datetime import datetime
import time
import os
import tkinter
from tkinter import messagebox
import webbrowser

BANNED_PROCESS_FILE = "./banned.csv"
RESULT_DIRECTORY = "./assets/result/"
TEST_DURATION = 30  # Minutes
start_time = None
finish_time = None

test_finished = False
monitor_processes_thread = None
monitor_time_thread = None

CHEATING_FLAG = False
TEST_NOT_FINISHED_ON_TIME_FLAG = False

NORMAL_ACTIVITY = 0
CHEATING_ID = 1
TEST_NOT_FINISHED_ON_TIME_ID = 2
CHEATING_AND_TEST_NOT_FINISHED_ON_TIME = 3

START_TIME = "15:43"
END_TIME = "16:50"

banned_processes_founded = []

btn_start_test, btn_finish_test = None, None

full_name_entry = None
user_full_name = ""


def create_result_file(id):
    global finish_time, banned_processes_founded
    global user_full_name
    ts = datetime.timestamp(finish_time)
    filename = f"0{id}_{ts}"
    file = open(RESULT_DIRECTORY+filename, "w+")
    file.write(f"n: {user_full_name}\n")
    file.write(f"s:{start_time}\nf:{finish_time}\n")
    file.write(f"b: {','.join(banned_processes_founded)}\n")
    # file.write(f"Late: {TEST_NOT_FINISHED_ON_TIME_FLAG}")
    file.close()
    print("Bye...")


def process_exists(process):
    # Create temporal file with process active
    com = f"tasklist | findstr {process} > tmp"
    os.system(com)
    print(com)

    # Get Size of the file created
    file_size = os.path.getsize("./tmp")
    print(f"File size {file_size}")

    if file_size == 0:
        return False
    else:
        return True


def get_banned_processes():
    banned_processes_df = pd.read_csv(BANNED_PROCESS_FILE)
    banned_processes = []
    for process in banned_processes_df.iterrows():
        banned_processes.append(process[1][0])

    return banned_processes


def monitor_processes(first_scan=False):
    global test_finished, CHEATING_FLAG, banned_processes_founded
    while not test_finished:
        banned_processes = get_banned_processes()
        for banned_process in banned_processes:
            if process_exists(banned_process):
                if banned_process not in banned_processes_founded:
                    messagebox.showerror(
                        title="Se ha abierto un proceso no permitido",
                        message="Se reportara esta acción. El proceso es: {}".format(banned_process))
                    banned_processes_founded.append(banned_process)
                if not CHEATING_FLAG:
                    CHEATING_FLAG = True
                    print(f"{banned_process} exist")
        if first_scan:
            time.sleep(0.2)
            break
        else:
            time.sleep(2)


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
            print(f"Total minutes: {total_test_minutes}")

        if total_test_minutes == TEST_DURATION:
            print("THE TEST HAS FINISHED")
            if not TEST_NOT_FINISHED_ON_TIME_FLAG:
                TEST_NOT_FINISHED_ON_TIME_FLAG = True


def start_test():
    global monitor_processes_thread, monitor_time_thread
    global btn_start_test, btn_finish_test
    global full_name_entry
    global user_full_name

    if len(full_name_entry.get()) > 15 and full_name_entry.get() != "Nombre Completo":
        user_full_name = full_name_entry.get()
        btn_start_test.config(state="disabled")
        btn_finish_test.config(state="normal")
        full_name_entry.config(state="disabled")

        monitor_time_thread.start()
        monitor_processes_thread.start()
    else:
        messagebox.showerror(
            title="Error al iniciar la prueba",
            message="Por favor intruduce tu nombre completo"
        )


def upload_test():
    webbrowser.open("www.google.com", new=2)


def finish_test():
    global monitor_processes_thread, monitor_time_thread, test_finished, window, start_time, finish_time
    global START_TIME, END_TIME

    end_time_hour = int(END_TIME.split(":")[0])
    end_time_minute = int(END_TIME.split(":")[1])
    now = datetime.now()
    actual_hour = now.hour
    actual_minute = now.minute

    if actual_hour >= end_time_hour and actual_minute >= end_time_minute:
        finish_time = datetime.now()

        test_finished = True
        if monitor_processes_thread is not None:
            monitor_processes_thread.join()
        if monitor_time_thread is not None:
            monitor_time_thread.join()
        window.destroy()

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


def main():
    # Thread setup
    global monitor_processes_thread, monitor_time_thread, window
    global START_TIME, END_TIME
    global banned_processes_founded
    global btn_start_test, btn_finish_test
    global full_name_entry

    monitor_processes_thread = threading.Thread(target=monitor_processes)
    monitor_time_thread = threading.Thread(target=monitor_time)

    # Configure window
    window = tkinter.Tk()
    window.title("Secure Exam")
    window.geometry("600x400")
    window.resizable(False, False)

    monitor_processes(first_scan=True)
    if len(banned_processes_founded) > 0:
        messagebox.showerror(
            title="No se puede iniciar la prueba",
            message="Cerrar los siguientes procesos: {}".format(", ".join(banned_processes_founded))
        )
        window.destroy()

    else:

        end_time_hour = int(END_TIME.split(":")[0])
        end_time_minute = int(END_TIME.split(":")[1])

        start_time_hour = int(START_TIME.split(":")[0])
        start_time_minute = int(START_TIME.split(":")[1])
        now = datetime.now()

        actual_hour = now.hour
        actual_minute = now.minute

        if end_time_hour <= actual_hour >= start_time_hour and\
            (actual_minute >= start_time_minute or actual_minute < end_time_minute ):


            # Configure buttons
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
                command=upload_test
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

            full_name_str_var = tkinter.StringVar(value="Nombre Completo")
            full_name_entry = tkinter.Entry(window,
                                            textvar=full_name_str_var,
                                            justify="center",
                                            state="normal"
                                            )
            full_name_entry.place(
                x=150,
                y=50,
                width=300,
                height=40
            )

            full_name_entry.focus_set()

            # Initial message

            messagebox.showinfo(title="Bienvenido",
                                message="Esto es un entorno seguro para realizar examenes."\
                                "No esta permitido el uso de cualquier herramienta que pueda ser"\
                                "utilizada para hacer trampa")

            window.focus_force()
            window.protocol("WM_DELETE_WINDOW", finish_test)
            window.mainloop()
        else:
            messagebox.showerror(
                "Error al abrir la prueba","La hora actual no concuerda"\
                " con la hora de la prubea que es de: {} a {}".format(START_TIME,END_TIME)
            )

            window.destroy()


if __name__ == "__main__":
    main()
