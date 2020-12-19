
from datetime import datetime
from pathlib import Path
import logging
import os
import sqlite3


# Definición de directorios de los archivos
RESULT_DIRECTORY = str(Path.home()).replace("\\", "/")+"/.anca/assets/log/"
DB_DIR = str(Path.home()).replace("\\", "/")+"/.anca/assets/"


# Creación de la clase LogFile
class LogFile:

    # Inicialización del objeto
    def __init__(self):
        # Crea objeto conexión y cursor para manipulación de BD
        con, cursor = self.con_database()
        # Intenta crear base de datos si no existe
        try:
            cursor.execute(''' CREATE TABLE student 
                        (name text, _group text, start_datetime text,
                        end_datetime text, cheated integer, usb_plugged integer, on_time integer, last_scanned text)
                ''')
            cursor.execute("INSERT INTO student VALUES (' ',' ',' ',' ', 0, 0, 1, ' ')")
            con.commit()
            con.close()
        except Exception as e:
            print(e)

        # Obtiene los archivos del directorio de resultados
        files = os.listdir(RESULT_DIRECTORY)

        # Si no existen archivos crea el archivo log en caso contrario lo asigna al nombre del archivo de la clase
        if len(files) == 0:
            self.filename = f"f_{datetime.timestamp(datetime.now())}"
        else:
            self.filename = files[0]

    # Método para conecar a la base de datos a partir del directorio definido para BD
    # Retorna objeto de conexión y cursor
    @staticmethod
    def con_database():
        con = sqlite3.connect(f"{DB_DIR}/student.db")
        cursor = con.cursor()
        return con, cursor

    # Método para actualizar campos de la basde de datos sqlite
    # Recibe como parametro el nombre del campo y el valor de este
    def set_db_field(self, field, value):
        # Crea objeto conexión y cursor para manipulación de BD
        con, cursor = self.con_database()
        # Intenta realizar operaciones en la BD
        try:
            # Inserta valor dependiendo si es entero o cadena de caracteres
            if type(value) is int:
                cursor.execute(f"UPDATE student set {field} = {value}")
            else:
                cursor.execute(f"UPDATE student set {field} = '{value}'")
            # Guarda cambios en BD y cierra conexión
            con.commit()
            con.close()
            # print("Campo actualizado")
            return True

        # Captura error y termina conexión
        except Exception as e:
            print(e)
            print("Error setting field on DB")
            con.close()
            return False

    # Método para escribir información en archivo de texto
    # Recibe como parametros la cadena de caracteres(data) y el nombre del
    # archivo (filename=None) que por defecto es None
    def write_data(self, data, filename=None):
        # Inicializa la variable file
        file = None
        # Intenta escribir en archivo
        try:
            # Si el nombre del archivo no es None se procede a abrir el archivo con ese misma variable
            if filename is not None:
                file = open(RESULT_DIRECTORY+filename, "w")
            # Si no se escribio un nombre de archivo se utiliza el nombre guardado al inicializar el objeto
            else:
                file = open(RESULT_DIRECTORY+self.filename, "a")
            # Escribe información pasada
            file.write(data)
            logging.info(f"The data: '{data}' has been written down")
        # Captura error de escritura/apertura de archivo
        except Exception as e:
            print(e)
            logging.error("Error writing data in file")
        # Cierra la escritura del archivo
        file.close()

    # Método para agregar un proceso prohibido en el archivo log y la BD
    def add_banned_process(self, process_data):
        # Obtiene detalle archivo
        name = process_data['name']
        alias = process_data['alias']
        time = process_data['time']
        # Escribe información en el archivo log
        self.write_data(f"Process: {name}, Alias: {alias}, Time: {time}\n")
        # Escribe información en la BD
        self.set_db_field("cheated", 1)

    # Método para agregar un dispositivo USB/SD al archivo log y BD
    def add_media_connected(self, dev_caption):
        # Escribe información en el archivo log
        self.write_data(f"Dev: {dev_caption}, Datetime: {datetime.now().isoformat()}\n")
        # Escribe información en la BD
        self.set_db_field("usb_plugged", 1)

    # Método para agregar el retraso en término de la prueba en archivo log y BD
    def add_no_on_time(self):
        # Escribe información en el archivo log
        # self.write_data(f"Dev: {dev_caption}, Datetime: {datetime.now().isoformat()}\n")
        # Escribe información en la BD
        self.set_db_field("on_time", 0)

    # Método para agregar el nombre del usuario al archivo log y BD
    def add_username(self, username):
        # Escribe información en el archivo log
        self.write_data(f"Username: {username}\n")
        # Escribe información en la BD
        self.set_db_field("name", username)

    # Método para agregar el grupo al archivo log y BD
    def add_group(self, group):
        # Escribe información en el archivo log
        self.write_data(f"Group: {group}\n")
        # Escribe información en la BD
        self.set_db_field("_group", group)

    # Mpetodo para agregar actividad a la BD
    def add_activity(self):
        last_scanned = datetime.now().isoformat()
        # self.write_data(f"Last scanned: {last_scanned}\n", self.last_scanned_file_name)
        # Escribe información en la BD
        self.set_db_field("last_scanned", last_scanned)

    # Método para agregar fecha y hora de termino de la prueba en el archivo log y BD
    def add_finish_time(self, finished_hour):
        # Escribe información en el archivo log
        self.write_data(f"Finished: {finished_hour}\n")
        # Escribe información en la BD
        self.set_db_field("end_datetime", finished_hour)

    # Método para agregar fecha y hora de inicio de la prueba en el archivo log y BD
    def add_start_time(self, start_hour):
        # Escribe información en el archivo log
        self.write_data(f"Start: {start_hour}\n")
        # Escribe información en la BD
        self.set_db_field("start_datetime", start_hour)

    # Método para agregar nombre de archivo de prueba en el archivo log
    def add_test(self, test_path):
        # Escribe información en el archivo log
        self.write_data(f"Test path: {test_path}\n")

    # Método para obtener nombre del usuario desde la BD
    # retorna cadena de caracteres
    def get_username(self):
        con, cursor = self.con_database()
        r = cursor.execute("SELECT name FROM student")
        username = (r.fetchone())[0]
        print(f"username: {username}")
        con.close()
        return username
