# coding=utf-8

import threading
import api_server
import utilities
import progress_data

server_thread = None


def start_server_threaded():
    global server_thread
    server_thread = threading.Thread(target=api_server.start_server, daemon=True)
    server_thread.start()


def stop_server_threaded():
    global server_thread
    server_thread.join(timeout=2)


# _res = input("Duration? (6)")
# if _res is None or _res == "":
#     _res = "6"
# _res = utilities.get_int(_res)

start_server_threaded()
start_progress_data = progress_data.get_start_progress_data("x")
start_progress_data['textFill'] = 0.25
start_progress_data['linearFill'] = 0.25
start_progress_data['circularFill'] = 0.25
progress_data.add_eye_tracking_stop(start_progress_data, 'p0', '0')
api_server.update_server_data(start_progress_data)

utilities.sleep_seconds(3)

stop_server_threaded()
