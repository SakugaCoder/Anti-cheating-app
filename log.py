
from datetime import datetime
from pathlib import Path
import logging
import os
import pyAesCrypt
import sqlite3
import tarfile
import time
import shutil

RESULT_DIRECTORY = str(Path.home()).replace("\\", "/")+"/.anca/assets/log/"
DB_DIR = str(Path.home()).replace("\\", "/")+"/.anca/assets/"

class LogFile:

    def __init__(self):
        con, cursor = self.con_database()
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

        files = os.listdir(RESULT_DIRECTORY)

        if len(files) == 0:
            self.filename = f"f_{datetime.timestamp(datetime.now())}"
        else:
            self.filename = files[0]


    def con_database(self):
        con = sqlite3.connect(f"{DB_DIR}/student.db")
        cursor = con.cursor()
        return con, cursor

    def set_db_field(self, field, value):
        con, cursor = self.con_database()
        try:
            if type(value) is int:
                cursor.execute(f"UPDATE student set {field} = {value}")
            else:
                cursor.execute(f"UPDATE student set {field} = '{value}'")
            con.commit()
            con.close()
            # print("Campo actualizado")
            return True

        except Exception as e:
            print("Error setting field on DB")
            con.close()
            return False

    def write_data(self, data, filename=None):
        file = None
        try:
            if filename is not None:
                file = open(RESULT_DIRECTORY+filename, "w")
            else:
                file = open(RESULT_DIRECTORY+self.filename, "a")
            file.write(data)
            logging.info(f"The data: '{data}' has been written down")
        except Exception as e:
            logging.error("Error writing data in file")
        file.close()

    def add_banned_process(self, process_data):
        name = process_data['name']
        alias = process_data['alias']
        time = process_data['time']
        self.write_data(f"Process: {name}, Alias: {alias}, Time: {time}\n")
        self.set_db_field("cheated", 1)

    def add_media_connected(self, dev_caption):
        self.write_data(f"Dev: {dev_caption}, Datetime: {datetime.now().isoformat()}\n")
        self.set_db_field("usb_plugged", 1)

    def add_no_on_time(self):
        # self.write_data(f"Dev: {dev_caption}, Datetime: {datetime.now().isoformat()}\n")
        self.set_db_field("on_time", 0)
        print("Setting on time false")

    def add_username(self, username):
        self.write_data(f"Username: {username}\n")
        self.set_db_field("name", username)

    def add_group(self, group):
        self.write_data(f"Group: {group}\n")
        self.set_db_field("_group", group)

    def add_activity(self):
        last_scanned = datetime.now().isoformat()
        # self.write_data(f"Last scanned: {last_scanned}\n", self.last_scanned_file_name)
        self.set_db_field("last_scanned", last_scanned)

    def add_finish_time(self, finished_hour):
        self.write_data(f"Finished: {finished_hour}\n")
        self.set_db_field("end_datetime", finished_hour)

    def add_start_time(self, start_hour):
        self.write_data(f"Start: {start_hour}\n")
        self.set_db_field("start_datetime", start_hour)

    def add_test(self, test_path):
        self.write_data(f"Test path: {test_path}\n")

    def get_username(self):
        con, cursor = self.con_database()
        r = cursor.execute("SELECT name FROM student")
        username = (r.fetchone())[0]
        print(f"username: {username}")
        con.close()
        return username


def decript_file(file_path):
    file_name = file_path.split('.aes')[0]
    file_path = "Exams/"+file_path
    buffer_size = 1024 * 64
    password = "secret"
    enc_file_size = os.stat(file_path).st_size
    # decrypt
    with open(file_path, "rb") as fIn:
        try:
            with open(f"Exams/Results/{file_name}.tar", "wb") as fOut:
                # decrypt file stream
                pyAesCrypt.decryptStream(fIn, fOut, password, buffer_size, enc_file_size)
        except ValueError:
            # remove output file on error
            os.remove(f"Exams/Results/{file_name}.tar")


def decrypt_files():
    files = os.listdir('Exams')
    try:
        os.mkdir("Exams/Results/")
    except Exception as e:
        print(e)
    for file in files:
        file_name = file.split(".aes")[0]
        decript_file(f'{file}')

        time.sleep(0.5)
        tar_filename = "Exams/Results/"+file.split(".aes")[0]+".tar"
        current_tar = tarfile.open(tar_filename)

        dir_name = f'./Exams/Results/{file_name}'
        current_tar.extractall(dir_name)
        current_tar.close()
        os.remove(tar_filename)

        time.sleep(0.5)
        username = os.listdir(f'Exams/Results/{file_name}/Users/')[0]
        db_path = f'Exams/Results/{file_name}/Users/{username}/.anca/assets/student.db'

        con = sqlite3.connect(db_path)
        cursor = con.cursor()
        r = cursor.execute("SELECT * FROM student")
        res = r.fetchone()
        group = res[1]
        cheated = res[4]
        usb_plugged = res[5]

        con.close()

        bad_behavior = True if cheated or usb_plugged else False

        group_folder = f"Exams/Results/{group}/"
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

#decrypt_files()