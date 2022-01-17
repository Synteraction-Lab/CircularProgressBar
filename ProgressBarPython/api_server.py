# coding=utf-8

import flask
from flask import request, jsonify
import time
from queue import Queue

PORT = 8080
HOST = '0.0.0.0'

# e.g. curl http://127.0.0.1:8080/data

app = flask.Flask(__name__)
app.config["DEBUG"] = False

data_queue = Queue()
last_request_time = 0
last_request_data = {}


@app.route('/', methods=['GET'])
def home_page():
    return "<h1>Server Running</h1>"


@app.route('/data', methods=['GET'])
def home():
    global data_queue, last_request_time, last_request_data

    if not data_queue.empty():
        last_request_data = data_queue.get()

    last_request_time = time.time()
    print_data('[Request]', last_request_data)
    return jsonify(last_request_data)


def start_server():
    app.run(host=HOST, port=PORT)


def stop_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def update_server_data(data):
    global data_queue
    data_queue.put(data)
    print_data('[Update]', data)


def print_data(message, data):
    print(f'{message} data: p = {data.get("progress")}, shown = {get_progress_display_value(data): .2f}, {data.get("progressText")}')


def get_progress_display_value(progress_object):
    if progress_object is None:
        return 0
    linear_val = progress_object.get('circularFill')
    circular_val = progress_object.get('linearFill')
    text_val = progress_object.get('textFill')

    if linear_val is None or circular_val is None or text_val is None:
        return 0
    elif linear_val != 0:
        return linear_val
    elif circular_val != 0:
        return circular_val
    elif text_val != 0:
        return text_val
    else:
        return 0


# start_server()

def get_server_request_data():
    return last_request_data.copy()


def get_server_request_time():
    return last_request_time


def get_pending_request_count():
    return data_queue.qsize()
