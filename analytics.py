import tkinter
from tkinter.filedialog import askdirectory

import os
import shutil
import pyAesCrypt
import time
import tarfile
import sqlite3


class AnalyticsUI():

    def __init__(self):
        self.master = tkinter.Tk()
        self.master.resizable(False, False)
        self.title = 'Analytics'
        self.geometry = '1100x600'
        self.dir_name = ''

        self.group = ''
        self.student = ''

        # Label for main folder
        self.textvar_label_main_folder = tkinter.StringVar(self.master, value='Directorio')
        self.label_main_folder = tkinter.Label(
            self.master,
            textvar=self.textvar_label_main_folder,
            bg='#2d2d2d',
            fg='#ffffff'
        )
        self.label_main_folder.place(x=50, y=10, width=300, height=20)

        # Cheated label
        cheated_label = tkinter.Label(self.master, text='Trampa')
        cheated_label.place(x=50, y=40)

        self.cheated_indicator = tkinter.Label(self.master, bg='gray')
        self.cheated_indicator.place(x=110, y=40, width=20, height=20)

        # USB connected label
        usb_connected_label = tkinter.Label(self.master, text='USB')
        usb_connected_label.place(x=140, y=40)

        self.usb_connected_indicator = tkinter.Label(self.master, bg='gray')
        self.usb_connected_indicator.place(x=180, y=40, width=20, height=20)

        # On time label
        on_time_label = tkinter.Label(self.master, text='A tiempo')
        on_time_label.place(x=220, y=40)

        self.on_time_indicator = tkinter.Label(self.master, bg='gray')
        self.on_time_indicator.place(x=280, y=40, width=20, height=20)

        # Button select directory
        button_add_directory = tkinter.Button(self.master, text='Seleccionar directorio', command=self.open_folder)
        button_add_directory.place(x=50, y=100, width=300, height=40)

        # Button decrypt
        self.button_process_exams = tkinter.Button(self.master, text='Procesar examenes', command=self.decrypt_files,
                                              state='disabled')
        self.button_process_exams.place(x=50, y=150, width=300, height=40)

        # Group list
        label_group = tkinter.Label(self.master, text='Selecciona grupo')
        label_group.place(x=50, y=210)

        self.listbox_group = tkinter.Listbox(self.master)
        self.listbox_group.place(x=50, y=240, width=300, height=100)
        self.listbox_group.bind('<<ListboxSelect>>', self.onselect_group)

        scrollbar_group = tkinter.Scrollbar(self.master, command=self.listbox_group.yview())
        self.listbox_group.config(yscrollcommand=scrollbar_group.set)
        scrollbar_group.place(x=350, y=240, height=100)

        # Student list
        label_student = tkinter.Label(self.master, text='Selecciona estudiante')
        label_student.place(x=50, y=390)

        self.listbox_student = tkinter.Listbox(self.master)
        self.listbox_student.place(x=50, y=420, width=300, height=100)
        self.listbox_student.bind('<<ListboxSelect>>', self.onselect_student)

        scrollbar_student = tkinter.Scrollbar(self.master)
        scrollbar_student.config(command=self.listbox_student.yview)
        scrollbar_student.place(x=350, y=420, height=100)
        self.listbox_student.config(yscrollcommand=scrollbar_student.set)

        # Log file text area
        self.textarea_logfile = tkinter.Text(self.master)
        self.textarea_logfile.place(x=400, y=10, width=680, height=580)

        scrollbar_textarea = tkinter.Scrollbar(self.master)
        scrollbar_textarea.config(command=self.textarea_logfile.yview)
        scrollbar_textarea.place(x=1080, y=10, height=580)

        """
        scrollbar_textarea_x = tkinter.Scrollbar(self.master, orient='horizontal')
        scrollbar_textarea_x.config(command=self.textarea_logfile.xview)
        scrollbar_textarea_x.place(x=400, y=580, width=480)
        """
        self.textarea_logfile.config(yscrollcommand=scrollbar_textarea.set)


    def onselect_group(self, evt):
        actual_students = self.listbox_student.size()

        try:
            self.group = self.listbox_group.get(self.listbox_group.curselection()[0])
            if actual_students > 0:
                self.listbox_student.delete(0, actual_students - 1)
                self.master.update()

            self.fill_student_data(self.group)
            print(self.group)

        except Exception as e:
            print("Anything selected")


    def onselect_student(self, evt):
        try:
            self.student = self.listbox_student.get(self.listbox_student.curselection())
            print(self.student)
            self.show_log_file()
        except Exception as e:
            print('Group selected')


    def show_log_file(self):
        if len(self.group) > 0 and len(self.student) > 0:
            self.cheated_indicator.config(bg='green')
            self.usb_connected_indicator.config(bg='green')
            self.on_time_indicator.config(bg='green')

            student_dir = f"{self.dir_name}/Results/{self.group}/trampa/{self.student}/Users/"
            student_username = os.listdir(student_dir)[0]

            log_dir = f"{student_dir}/{student_username}/.anca/assets/log/"
            log_file = os.listdir(log_dir)[0]
            db_path = f"{student_dir}/{student_username}/.anca/assets/student.db"

            con = sqlite3.connect(db_path)
            cursor = con.cursor()
            r = cursor.execute("SELECT * FROM student")
            res = r.fetchone()

            cheated = res[4]
            usb_plugged = res[5]
            on_time = res[6]

            if cheated == 1:
                self.cheated_indicator.config(bg='green')
            else:
                self.cheated_indicator.config(bg='red')

            if usb_plugged == 1:
                self.usb_connected_indicator.config(bg='green')
            else:
                self.usb_connected_indicator.config(bg='red')

            if on_time == 0:
                self.on_time_indicator.config(bg='green')
            else:
                self.on_time_indicator.config(bg='red')

            con.close()
            with open(log_dir+log_file, 'r') as lf:
                self.textarea_logfile.delete('1.0', "end")
                lines = lf.readlines()
                index = 1
                for l in lines:
                    self.textarea_logfile.insert("end", l)
                    index += 1
                print(l)

            print(student_username)


    def open_folder(self):
        dir_name = askdirectory(
            initialdir="./",
            title="Selecciona el directorio"
        )
        print(f"Dir is: {dir_name}")
        self.textvar_label_main_folder.set(dir_name)
        self.dir_name = dir_name
        if len(dir_name) > 0:
            self.button_process_exams.config(state='normal')

    def init_ui(self):
        self.master.title(self.title)
        self.master.geometry(self.geometry)
        self.master.mainloop()

    def decrypt_file(self, file_path):
        file_name = file_path.split('.aes')[0]
        file_path = f"{self.dir_name}/"+file_path
        print(f"File path: {file_path}")
        buffer_size = 1024 * 64
        password = "secret"
        enc_file_size = os.stat(file_path).st_size
        # decrypt
        with open(file_path, "rb") as fIn:
            try:
                with open(f"{self.dir_name}/Results/{file_name}.tar", "wb") as fOut:
                    # decrypt file stream
                    pyAesCrypt.decryptStream(fIn, fOut, password, buffer_size, enc_file_size)
            except ValueError:
                # remove output file on error
                os.remove(f"{self.dir_name}/Results/{file_name}.tar")

    def decrypt_files(self):
        self.textvar_label_main_folder.set('Procesando examenes...')
        self.label_main_folder.config(bg='orange')

        time.sleep(2)
        files = os.listdir(self.dir_name)
        try:
            os.mkdir(f"{self.dir_name}/Results/")
        except Exception as e:
            print(e)
            shutil.rmtree(f"{self.dir_name}/Results/")
            files = os.listdir(self.dir_name)
            os.mkdir(f"{self.dir_name}/Results/")
        for file in files:

            file_name = file.split(".aes")[0]
            self.decrypt_file(f'{file}')

            time.sleep(0.5)
            tar_filename = f"{self.dir_name}/Results/"+file.split(".aes")[0]+".tar"
            current_tar = tarfile.open(tar_filename)

            dir_name = f'{self.dir_name}/Results/{file_name}'
            current_tar.extractall(dir_name)
            current_tar.close()
            os.remove(tar_filename)

            time.sleep(0.5)
            username = os.listdir(f'{self.dir_name}/Results/{file_name}/Users/')[0]
            db_path = f'{self.dir_name}/Results/{file_name}/Users/{username}/.anca/assets/student.db'

            con = sqlite3.connect(db_path)
            cursor = con.cursor()
            r = cursor.execute("SELECT * FROM student")
            res = r.fetchone()
            group = res[1]
            cheated = res[4]
            usb_plugged = res[5]
            on_time = res[6]

            con.close()

            bad_behavior = True if cheated or usb_plugged or on_time == 0 else False

            group_folder = f"{self.dir_name}/Results/{group}/"
            try:
                os.mkdir(group_folder)
                os.mkdir(group_folder+"/trampa")
                os.mkdir(group_folder+"/normal")

            except Exception as e:
                # Grupo ya existe
                print(e)

            if bad_behavior:
                shutil.move(dir_name, group_folder+"/trampa")
            else:
                shutil.move(dir_name, group_folder + "/normal")

            print(res)
            con.close()

        self.textvar_label_main_folder.set('Examenes procesados')
        self.label_main_folder.config(bg='green')
        self.fill_group_data()

    def fill_student_data(self, group):
        students_dir = f'{self.dir_name}/Results/{group}/trampa'
        students = os.listdir(students_dir)
        index = 0
        for student in students:
            self.listbox_student.insert(index, student)

        self.master.update()

    def get_student_log(self):
        group = self.listbox_group.get(self.listbox_student.curselection())
        student = self.listbox_student.get(self.listbox_student.curselection())
        print(f"Group: {group}, Student: {student}")

    def fill_group_data(self):
        groups = os.listdir(f"{self.dir_name}/Results")
        index = 0
        for group in groups:
            self.listbox_group.insert(index, group)
            index += 1

        self.master.update()


ui = AnalyticsUI()
ui.init_ui()