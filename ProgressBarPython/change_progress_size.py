# coding=utf-8

import sys
import threading
import api_server
import progress_data
import utilities

DEFAULT_PROGRESS_SIZE_CIRCULAR = 0.32
DEFAULT_PROGRESS_SIZE_LINEAR = 0.40
DEFAULT_PROGRESS_SIZE = DEFAULT_PROGRESS_SIZE_CIRCULAR
DEFAULT_PROGRESS_DEPTH = 1.6


server_thread = None


def start_server_threaded():
    global server_thread
    server_thread = threading.Thread(target=api_server.start_server, daemon=True)
    server_thread.start()


def stop_server_threaded():
    global server_thread
    server_thread.join(timeout = 6)


start_server_threaded()
print("starting server")
# utilities.sleep_seconds(1)

api_server.update_server_data(progress_data.get_start_progress_data('configure'))


_type = ''
while _type != 'n':
    _type = input("Continue? (c/l/d/r/n)")

    if _type == 'l' or _type == 'c' or _type =='s' or _type == 'd':
        _size = input('size:')
        size = float(_size)

        progress = progress_data.get_start_progress_data(_type, _size)
        if _type == 'l':
            progress_data.add_change_size(progress, size, DEFAULT_PROGRESS_SIZE_CIRCULAR)
        if _type == 'c':
            progress_data.add_change_size(progress, DEFAULT_PROGRESS_SIZE_LINEAR, size)
        if _type == 's':
            progress_data.add_change_size(progress, size, size)
        if _type == 'd':
            progress_data.add_change_depth(progress, size)
        # send with configuration
        api_server.update_server_data(progress)
        # send without configuration
        api_server.update_server_data(progress_data.get_start_progress_data(_type, _size))

    if _type == 'r':
        progress = progress_data.get_start_progress_data('reset size', f'{DEFAULT_PROGRESS_SIZE:.2f}')
        progress_data.add_change_size(progress, DEFAULT_PROGRESS_SIZE_LINEAR, DEFAULT_PROGRESS_SIZE_CIRCULAR)
        api_server.update_server_data(progress)

        progress = progress_data.get_start_progress_data('reset depth', f'{DEFAULT_PROGRESS_DEPTH:.2f}')
        progress_data.add_change_depth(progress, DEFAULT_PROGRESS_DEPTH)
        api_server.update_server_data(progress)
        
        api_server.update_server_data(progress_data.get_start_progress_data('default'))



# utilities.sleep_seconds(3)
print("stopping server")
stop_server_threaded()
