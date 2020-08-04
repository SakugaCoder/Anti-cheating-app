import logging
from datetime import datetime
import os
import pyAesCrypt
from pathlib import Path
RESULT_DIRECTORY = str(Path.home()).replace("\\","/")+"/.anca/assets/log/"


class LogFile:

    def __init__(self):
        files = os.listdir(RESULT_DIRECTORY)
        if len(files) == 2:
            if files[0].split("f") == 2:
                self.filename = files[0]
                self.last_scanned_file_name = files[1]
            else:
                self.filename = files[1]
                self.last_scanned_file_name = files[0]
        elif len(files) == 0:
            self.filename = f"f_{datetime.timestamp(datetime.now())}"
            self.last_scanned_file_name = f"s_{datetime.timestamp(datetime.now())}"

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

    def add_username(self, username):
        self.write_data(f"Username: {username}\n")

    def add_activity(self):
        self.write_data(f"Last scanned: {datetime.now().isoformat()}\n",self.last_scanned_file_name)

    def add_finish_time(self, finished_hour):
        self.write_data(f"Finished: {finished_hour}\n")

    def add_start_time(self, start_hour):
        self.write_data(f"Start: {start_hour}\n")

    def add_test(self, test_path):
        self.write_data(f"Test path: {test_path}\n")


def decript_file(file_path):
    buffer_size = 1024 * 64
    password = "secret"
    enc_file_size = os.stat(file_path).st_size
    # decrypt
    with open(file_path, "rb") as fIn:
        try:
            with open("decript.tar", "wb") as fOut:
                # decrypt file stream
                pyAesCrypt.decryptStream(fIn, fOut, password, buffer_size, enc_file_size)
        except ValueError:
            # remove output file on error
            os.remove("decript.tar")

#decript_file("C:/Users/HP/Desktop/encrypt.aes")