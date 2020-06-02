import threading
import pandas as pd
from datetime import datetime
import time

BANNED_PROCESS_FILE = "./banned.csv"


def get_banned_process():
    banned_process_df = pd.read_csv(BANNED_PROCESS_FILE)
    banned_process = []
    for process in banned_process_df.iterrows():
        banned_process.append(process[1][0])

    return banned_process


def monitor_proceess():
    banned_process = get_banned_process()
    while True:
        time.sleep(2)


def main():
    #monitor_process_thread = threading.Thread(target=monitor_proceess)
    #monitor_process_thread.start()
    while True:
        get_banned_process()
        time.sleep(2)


if __name__ == "__main__":
    main()