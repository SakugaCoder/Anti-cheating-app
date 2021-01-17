import tkinter
from tkinter.filedialog import askdirectory
from tkinter import messagebox
import os
import shutil
import pyAesCrypt
import time
import tarfile
import sqlite3


# Creación de clase AnalyticsUI
class AnalyticsUI:

    # Inicializa la clase
    def __init__(self):
        # Define la configuración de la ventana tamaño, nombre y restricción de cambio de tamaño
        self.master = tkinter.Tk()
        self.master.resizable(False, False)
        self.title = 'Analytics'
        self.geometry = '1100x600'
        self.dir_name = ''

        # Variables para almacenar el nombre y grupo del estudiante
        self.group = ''
        self.student = ''

        # Label para mostrar el directorio seleccionado
        self.textvar_label_main_folder = tkinter.StringVar(self.master, value='Directorio')
        self.label_main_folder = tkinter.Label(
            self.master,
            textvar=self.textvar_label_main_folder,
            bg='#2d2d2d',
            fg='#ffffff'
        )
        self.label_main_folder.place(x=50, y=10, width=300, height=20)

        # Label para 'trampa'
        cheated_label = tkinter.Label(self.master, text='Trampa')
        cheated_label.place(x=50, y=40)

        # Indicador para trampa
        self.cheated_indicator = tkinter.Label(self.master, bg='gray')
        self.cheated_indicator.place(x=110, y=40, width=20, height=20)

        # Label para 'USB'
        usb_connected_label = tkinter.Label(self.master, text='USB')
        usb_connected_label.place(x=140, y=40)

        # Indicador apra 'USB'
        self.usb_connected_indicator = tkinter.Label(self.master, bg='gray')
        self.usb_connected_indicator.place(x=180, y=40, width=20, height=20)

        # Label para 'A tiempo'
        on_time_label = tkinter.Label(self.master, text='A tiempo')
        on_time_label.place(x=220, y=40)

        # Indicador para 'A tiempo'
        self.on_time_indicator = tkinter.Label(self.master, bg='gray')
        self.on_time_indicator.place(x=280, y=40, width=20, height=20)

        # Entrada de texto para hora validar hora inicio
        start_datetime_label = tkinter.Label(self.master, text='Inicio')
        start_datetime_label.place(x=50, y=70, width=28, height=20)

        start_datetime_tv = tkinter.StringVar(master=self.master, value='2021-01-17 15:00')
        self.start_datetime_entry = tkinter.Entry(self.master, textvar=start_datetime_tv)
        self.start_datetime_entry.place(x=85, y=70, width=100, height=20)

        # Entrada de texto para hora validar hora final
        end_datetime_label = tkinter.Label(self.master, text='Fin')
        end_datetime_label.place(x=200, y=70, width=28, height=20)

        end_datetime_tv = tkinter.StringVar(master=self.master, value='2021-01-17 16:00')
        self.end_datetime_entry = tkinter.Entry(self.master, textvar=end_datetime_tv)
        self.end_datetime_entry.place(x=230, y=70, width=100, height=20)

        # Botón para seleccionar dicrectorio (abre cuadro de dialogo)
        button_add_directory = tkinter.Button(self.master, text='Seleccionar directorio', command=self.open_folder)
        button_add_directory.place(x=50, y=100, width=300, height=40)

        # Botón para procesar examenes (inicialmente bloqueado hasta seleccionad directorio)
        self.button_process_exams = tkinter.Button(self.master, text='Procesar examenes', command=self.decrypt_files,
                                              state='disabled')
        self.button_process_exams.place(x=50, y=150, width=300, height=40)

        # Label para 'Selecciona grupo'
        label_group = tkinter.Label(self.master, text='Selecciona grupo')
        label_group.place(x=50, y=210)

        # Listbox para almacenar los grupos disponibles
        self.listbox_group = tkinter.Listbox(self.master)
        self.listbox_group.place(x=50, y=240, width=300, height=100)
        self.listbox_group.bind('<<ListboxSelect>>', self.onselect_group)

        # Scrollbar para la listbox de los grupos
        scrollbar_group = tkinter.Scrollbar(self.master, command=self.listbox_group.yview())
        self.listbox_group.config(yscrollcommand=scrollbar_group.set)
        scrollbar_group.place(x=350, y=240, height=100)

        # Label para 'Selecciona estudiante'
        label_student = tkinter.Label(self.master, text='Selecciona estudiante')
        label_student.place(x=50, y=390)

        # Listbox para almacenar los estudiantes disponinbles
        self.listbox_student = tkinter.Listbox(self.master)
        self.listbox_student.place(x=50, y=420, width=300, height=100)
        self.listbox_student.bind('<<ListboxSelect>>', self.onselect_student)

        # Scrollbar para la listbox de los estudiantes
        scrollbar_student = tkinter.Scrollbar(self.master)
        scrollbar_student.config(command=self.listbox_student.yview)
        scrollbar_student.place(x=350, y=420, height=100)
        self.listbox_student.config(yscrollcommand=scrollbar_student.set)

        # Textarea para mostrar el archivo log de cada estudiante
        self.textarea_logfile = tkinter.Text(self.master)
        self.textarea_logfile.place(x=400, y=10, width=680, height=580)

        # Scrollbar para el textarea del archivo log
        scrollbar_textarea = tkinter.Scrollbar(self.master)
        scrollbar_textarea.config(command=self.textarea_logfile.yview)
        scrollbar_textarea.place(x=1080, y=10, height=580)
        self.textarea_logfile.config(yscrollcommand=scrollbar_textarea.set)

    # Método para el evento de selección de grupo (muestra estudiantes en ese grupo)
    def onselect_group(self, evt):
        # Obtiene el numero de estudiante actuales
        actual_students = self.listbox_student.size()

        # Trata de obtener la selección actual del grupo, si se genera error
        # es por que se ha deseleccionado el listbox de grupo
        try:
            # Guarda el nombre del grupo en una propieadad de la clase
            self.group = self.listbox_group.get(self.listbox_group.curselection()[0])
            # Si hay estudiantes en el listbox los elimina
            if actual_students > 0:
                self.listbox_student.delete(0, actual_students - 1)
                self.master.update()
            # Llama método para llenar el listbox con los estudiantes correspondientes al grupo
            self.fill_student_data(self.group)
            print(self.group)

        except Exception as e:
            print("Anything selected")

    # Método para el evento de selección de estudiante (muestra datos del estudiante)
    def onselect_student(self, evt):
        # Trata de obtener la selección actual, si se genera error es por que el listbox ha sido deseleccionado
        try:
            # Guarda el nombre del estudiante en una propiedad de la clase
            self.student = self.listbox_student.get(self.listbox_student.curselection())
            print(self.student)
            # Muestra el contenido del archivo log del estudiante
            self.show_log_file()
        except Exception as e:
            print('Group selected')

    # Método para mostrar el archivo log del estudiante seleccionado
    def show_log_file(self):
        # Solo procede si existe un grupo y estudiante seleccionado anteriormente
        if len(self.group) > 0 and len(self.student) > 0:

            # Establece los indicadores de eventos en verde
            self.cheated_indicator.config(bg='green')
            self.usb_connected_indicator.config(bg='green')
            self.on_time_indicator.config(bg='green')

            # Establece el directorio del estudiante y obtiene el username correspondiente
            student_dir = f"{self.dir_name}/Results/{self.group}/trampa/{self.student}/Users/"
            student_username = os.listdir(student_dir)[0]

            # Establece el directorio del log y de la base de datos
            log_dir = f"{student_dir}/{student_username}/.anca/assets/log/"
            log_file = os.listdir(log_dir)[0]
            db_path = f"{student_dir}/{student_username}/.anca/assets/student.db"

            # Crea conexión a base de datos
            con = sqlite3.connect(db_path)
            cursor = con.cursor()
            # Ejecuta consulta para obtener datos del estudiante en la BD
            r = cursor.execute("SELECT * FROM student")
            # Obtiene el resultado
            res = r.fetchone()

            # Obtiene campos del resultado obtenido
            cheated = res[4]
            usb_plugged = res[5]
            on_time = res[6]

            # Para cada campo verifica si es verdadero y en dado caso establece el indicador correpondiente
            # en color verde indicando que si existio actividad durante la prueba en el campo mostrado
            # en caso contradio cambia el indicador a un color rojo
            if cheated == 1:
                self.cheated_indicator.config(bg='red')
            else:
                self.cheated_indicator.config(bg='green')

            if usb_plugged == 1:
                self.usb_connected_indicator.config(bg='red')
            else:
                self.usb_connected_indicator.config(bg='green')

            if on_time == 0:
                self.on_time_indicator.config(bg='red')
            else:
                self.on_time_indicator.config(bg='green')

            # Cierra la conexión con la BD
            con.close()

            # Abre el archivo log correpondiente
            with open(log_dir+log_file, 'r') as lf:
                # Elimina el texto anterior del textarea para el archivo log
                self.textarea_logfile.delete('1.0', "end")
                # Lee todas las lineas de texto del archivo
                lines = lf.readlines()
                # Crea un índice para establecer cada linea dentro del textarea
                index = 1
                # Itera sobre las lineas obtenidas
                for l in lines:
                    # Agrega cada linea al textarea
                    self.textarea_logfile.insert("end", l)
                    # Incrementa el índice
                    index += 1
                # print(l)
            # print(student_username)

    # Método para obtener el directorio de los examenes
    def open_folder(self):
        # Abre cuadro de dialogo y almacena el directorio seleccionado en una variable
        dir_name = askdirectory(
            initialdir="./",
            title="Selecciona el directorio"
        )
        print(f"Dir is: {dir_name}")

        # Cambia el texto del Label para el directorio con el directorio seleccionado
        self.textvar_label_main_folder.set(dir_name)
        # Establece el nombre del directorio
        self.dir_name = dir_name
        # Si se selecciono un directorio correctamente
        if len(dir_name) > 0:
            # Activa botón para procesar examenes
            self.button_process_exams.config(state='normal')

    # Método para iniciar/mostrar la interfaz grafica
    def init_ui(self):
        self.master.title(self.title)
        self.master.geometry(self.geometry)
        self.master.mainloop()

    # Método para desencriptar un archivo, recibe como parametro la ruta del archivo
    def decrypt_file(self, file_path):
        # Obtiene el nombre del archivo
        file_name = file_path.split('.aes')[0]
        # Establece la ruta final del archivo
        file_path = f"{self.dir_name}/"+file_path
        print(f"File path: {file_path}")
        # Define el tamaño del buffer
        buffer_size = 1024 * 64
        # Define el password
        password = "secret"
        # Obtiene el tamaño del archivo a desencriptar
        enc_file_size = os.stat(file_path).st_size
        # Abre archivo encriptado
        with open(file_path, "rb") as fIn:
            # Trata de desencriptar el archivo con los parametros previamente establecidos
            try:
                # Crea un nuevo archivo para almacenar el archivo desencriptado
                with open(f"{self.dir_name}/Results/{file_name}.tar", "wb") as fOut:
                    # Función para desencriptar el archivo
                    pyAesCrypt.decryptStream(fIn, fOut, password, buffer_size, enc_file_size)
            # Si se encuentra un error se elimina el archivo tar previamente creado
            except ValueError:
                os.remove(f"{self.dir_name}/Results/{file_name}.tar")

    # Función para desencriptar multiples archivos
    def decrypt_files(self):
        self.listbox_student.delete(0, tkinter.END)
        self.listbox_group.delete(0, tkinter.END)
        if len(self.start_datetime_entry.get()) == 16 and len(self.end_datetime_entry.get()) == 16:
            # Establece label del directorio con mensaje 'Procesando examenes...'
            self.textvar_label_main_folder.set('Procesando examenes...')
            # Cambia color del label del directorio a un color naranja
            self.label_main_folder.config(bg='orange')

            # Espera 2 segundos
            # time.sleep(2)
            # Lista archivos en el directorio actual (seleccionado en cuadro de dialogo)
            files = os.listdir(self.dir_name)

            # Trata de crear directorio de resultados (si es que no existe)
            try:
                os.mkdir(f"{self.dir_name}/Results/")

            # Si se encuentra un error se procede a eliminar el directorio y volver a crearlo
            except Exception as e:
                # print(e)
                shutil.rmtree(f"{self.dir_name}/Results/")
                files = os.listdir(self.dir_name)
                os.mkdir(f"{self.dir_name}/Results/")

            # Itera sobre los archivos de la carpeta seleccionada
            for file in files:
                # Obtiene nombre del archivo
                file_name = file.split(".aes")[0]

                # Desencripta archivo
                self.decrypt_file(f'{file}')

                # Espera 0.5 segundos
                time.sleep(0.5)
                # Establece el nombre del archivo tar
                tar_filename = f"{self.dir_name}/Results/"+file.split(".aes")[0]+".tar"
                # Abre el archivo tar
                current_tar = tarfile.open(tar_filename)

                # Establece el nombre del directorio
                dir_name = f'{self.dir_name}/Results/{file_name}'
                # Extrae el archivo tar en el directorio seleccionado
                current_tar.extractall(dir_name)
                # Cierra archivo tar
                current_tar.close()
                # Elimina archivo tar
                os.remove(tar_filename)

                # Espera 0.5 segundos
                time.sleep(0.5)

                # Obtiene el username del archivo/estudiante actual
                username = os.listdir(f'{self.dir_name}/Results/{file_name}/Users/')[0]
                # Establece la dirección de la base de datos
                db_path = f'{self.dir_name}/Results/{file_name}/Users/{username}/.anca/assets/student.db'

                # Crea objeto de conexión a la base de datos
                con = sqlite3.connect(db_path)
                cursor = con.cursor()

                # Ejecuta consulta para obtener datos de estudiante
                r = cursor.execute("SELECT * FROM student")
                # Obtiene resultado
                res = r.fetchone()

                # Establece el resultado en cada campo correspondiente
                group = res[1]
                cheated = res[4]
                usb_plugged = res[5]
                on_time = res[6]

                start_dt = res[2]
                end_dt = res[3]

                # -----------------------------------
                print("################################")
                # Fecha y tiempo de inicio del estudiante
                start_date = start_dt.split('T')[0]
                start_time = (start_dt.split('T'))[1].split(':')
                start_time_hour = start_time[0]
                start_time_minute = start_time[1]
                start_time = int(start_time_hour+start_time_minute)

                print(f'Student start datetime: {start_date} - {start_time}')

                # Fecha y tiempo de termino del estudiante
                end_date = end_dt.split('T')[0]
                end_time = (end_dt.split("T")[1]).split(':')
                end_time_hour = end_time[0]
                end_time_minute = end_time[1]
                end_time = int(end_time_hour+end_time_minute)

                print(f'Student end datetime: {end_date} - {end_time}')

                # Fecha y tiempo de inicio a validar
                actual_start_datetime = self.start_datetime_entry.get()
                actual_start_date = actual_start_datetime.split(' ')[0]
                actual_start_time = actual_start_datetime.split(' ')[1]
                actual_hour_start = actual_start_time.split(":")[0]
                actual_minute_start = actual_start_time.split(":")[1]
                actual_start_time = int(actual_hour_start+actual_minute_start)

                print(f'Valid start datetime: {actual_start_date} - {actual_start_time}')

                # Tiempo final a validar
                actual_end_datetime = self.end_datetime_entry.get()
                actual_end_date = actual_end_datetime.split(' ')[0]
                actual_end_time = actual_end_datetime.split(' ')[1]
                actual_hour_end = actual_end_time.split(":")[0]
                actual_minute_end = actual_end_time.split(":")[1]
                actual_end_time = int(actual_hour_end+actual_minute_end)

                print(f'Valid end datetime: {actual_end_date} - {actual_end_time}')
                print("################################")

                # Verifica que el estudiante termino a tiempo
                on_datetime = False
                if start_date == actual_start_date == end_date:
                    if start_time >= actual_start_time and end_time <= actual_end_time:
                        on_datetime = True
                        print('Yeah a tiempo')
                    else:
                        print('Reprobado')
                else:
                    print('Reprobado')

                # Si no estuvo a tiempo actualiza la bd para que al procesar los archivos sqlite por separado
                # se pueda mostrar graficamente el estado
                try:
                    # Ejecuta consulta de actualización en la BD
                    cursor.execute(f"UPDATE student set on_time = {int(on_datetime)}")

                    # Guarda cambios en BD y cierra conexión
                    con.commit()
                    # print("Campo actualizado")

                    # Captura error y termina conexión
                except Exception as e:
                    print(e)
                    print("Error setting field on DB")
                # -----------------------------------

                # Cierra la conexión con la BD
                con.close()

                # Bandera para detectar trampa (compara los campos obtenidos de la BD)
                bad_behavior = True if cheated or usb_plugged or not on_datetime else False

                # Establece directorio para el nombre del grupo
                group_folder = f"{self.dir_name}/Results/{group}/"

                # Trata de crear directorios para grupo
                try:

                    os.mkdir(group_folder)
                    os.mkdir(group_folder+"/trampa")
                    os.mkdir(group_folder+"/normal")

                # Si se genera error indica que ya esta creado
                except Exception as e:
                    pass
                    # Grupo ya existe
                    # print(e)
                # Si el estudiante cuenta con mal comportamiento se mueve a carpeta 'trampa'
                # de lo contrario se mueve a carpeta 'normal' para realizar el filtrado
                if bad_behavior:
                    shutil.move(dir_name, group_folder+"/trampa")
                else:
                    shutil.move(dir_name, group_folder + "/normal")

                # print(res)

                # Cierra conexión
                con.close()

            # Establece label de directorio con mensaje de exito y cambia su color de fondo a verde
            self.textvar_label_main_folder.set('Examenes procesados')
            self.label_main_folder.config(bg='green')

            # Al finalizar llama al método para obtener los grupos
            self.fill_group_data()

        else:
            messagebox.showerror(
                title='Error',
                message='Favor de ingresar una fecha de inicio y fin valida'
            )

    # Método para llenar el listbox con nombres de los estudiantes del grupo seleccionado
    def fill_student_data(self, group):
        # Establece grupo de los estudiantes
        students_dir = f'{self.dir_name}/Results/{group}/trampa'
        # Obtiene las carpteas de cada estudiante
        students = os.listdir(students_dir)
        # Crea índice para establecer orden en listbox
        index = 0
        # Itera sobre las carpetas de los estudiantes
        for student in students:
            # Agrega estudiante a listbox para estudiantes
            self.listbox_student.insert(index, student)

        # Actualiza ventana
        self.master.update()

    # Método para obtener los grupos en el directorio seleccionado
    def fill_group_data(self):
        # Lista grupos en la carpeta de resultados
        groups = os.listdir(f"{self.dir_name}/Results")
        # Crea índice para establecer orden en listbox
        index = 0

        # Itera sobre todos los grupos encontrados
        for group in groups:
            # Agrega el grupo a listbox de grupos
            self.listbox_group.insert(index, group)
            # Incrementa el índice
            index += 1

        # Actualiza ventana
        self.master.update()


# Crea objeto de la clase AnalyticsUI
ui = AnalyticsUI()
# Inicializa ventana
ui.init_ui()
