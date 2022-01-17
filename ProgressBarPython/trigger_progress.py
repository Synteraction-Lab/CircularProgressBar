# coding=utf-8

import sys
import threading
import time
import traceback
from pynput import keyboard
import api_server
import utilities
from random import randint
from queue import Queue

import progress_data
import participant_config

PROGRESS_DISPLAY_START_DELAY_SECONDS = 1 * 15  # 60
PROGRESS_DISPLAY_START_WAIT_RANDOM_SECONDS = 20
TRAINING_START_DELAY_SHIFT = -20

PROGRESS_MAXIMUM_WAIT_IN_100_PERCENT_SECONDS = 45

TARGETS_DISPLAY_DURATION_SECONDS = 3
PROGRESS_DISPLAY_DURATION_SECONDS = 3  # 10

CONTINUOUS_PROGRESS_DISPLAY_DURATION_SECONDS = progress_data.PROGRESS_DISPLAY_UPDATE_SECONDS  # 3
INTERMITTENT_PROGRESS_DISPLAY_DURATION_SECONDS = PROGRESS_DISPLAY_DURATION_SECONDS
TRAINING_PROGRESS_DISPLAY_DURATION_SECONDS = 3

flag_is_running = False

last_key = None
last_key_press_time = 0
log_queue = Queue()


def keep_key_info(key, key_time):
    global last_key, last_key_press_time
    last_key = key
    last_key_press_time = key_time


DEBOUNCE_SECONDS = 0.2  # 200 ms


def is_key_already_pressed(key, key_time):
    if key == last_key and key_time - last_key_press_time < DEBOUNCE_SECONDS:
        return True
    return False


def on_press(key):
    global flag_is_running
    current_time = time.time()

    # print("Key: ", key)
    if key == keyboard.KeyCode.from_char('`') or key == keyboard.Key.esc:
        # cleaning up
        flag_is_running = False
        return False  # stop listener

    # debounce the keys
    if is_key_already_pressed(key, current_time):
        print('You have already pressed: ', key)
        return True

    if key == keyboard.Key.page_down or key == keyboard.Key.down:
        keep_key_info(key, current_time)
        log_events('R', current_time)

    if key == keyboard.Key.page_up or key == keyboard.Key.up:
        keep_key_info(key, current_time)
        log_events('O', current_time)


def save_log_file(participant, session):
    file_name = f'data/{participant}/{participant}_{session}_progress.csv'

    log_data = ''
    while not log_queue.empty():
        log_data += log_queue.get()

    try:
        utilities.append_data(file_name, log_data)
    except Exception:
        print("Unhandled exception")
        traceback.print_exc(file=sys.stdout)


def reset_log():
    with log_queue.mutex:
        log_queue.queue.clear()

    log_queue.put(
        'Event,Time,Progress,CircularProgress,LinearProgress,TextProgress,RequestTime,Extra\n')


def log_events(event, time, extra=''):
    print(f'Log event: {event}')
    current_data = api_server.get_server_request_data()
    data_request_time = api_server.get_server_request_time()
    log_queue.put(
        f'{event},'
        f'{time},'
        f'{current_data.get("progress", "")},'
        f'{current_data.get("circularFill", "")},'
        f'{current_data.get("linearFill", "")},'
        f'{current_data.get("textFill", "")},'
        f'{data_request_time},'
        f'{extra}\n'
    )


last_server_request_time = 0


def log_server_requests(extra_info=''):
    global last_server_request_time
    server_request_time = api_server.get_server_request_time()

    if server_request_time != last_server_request_time:
        last_server_request_time = server_request_time

        if extra_info == '':
            current_data = api_server.get_server_request_data()
            extra_info = current_data.get('config', '')

        log_events('SERVER_REQUEST', time.time(), extra_info)


def get_display_value(progress_object):
    return progress_data.get_progress_display_value(progress_object)


def get_next_update_gap(progress_type, is_training, progress_obj):
    is_continuous = progress_data.is_continuous(progress_type)

    if is_continuous:
        gap = CONTINUOUS_PROGRESS_DISPLAY_DURATION_SECONDS
    else:
        # intermittent
        if get_display_value(progress_obj) != 0:
            gap = INTERMITTENT_PROGRESS_DISPLAY_DURATION_SECONDS
        else:
            gap = CONTINUOUS_PROGRESS_DISPLAY_DURATION_SECONDS

    if is_training:
        gap = TRAINING_PROGRESS_DISPLAY_DURATION_SECONDS

    # print('gap: ', gap, ', progress obj: ', progress_obj)

    return gap


def start_progress_bar(participant, session):
    global flag_is_running

    if flag_is_running:
        print('Another instance is running')
        return

    flag_is_running = True

    # participant session
    progress_type = participant_config.get_type(participant, session)
    is_continuous = progress_data.is_continuous(progress_type)
    is_training = utilities.get_int(session) < 0
    is_learning = progress_data.is_learning(progress_type)

    targets_string, noises_string, progress_point_list = progress_data.get_progress_data(
        progress_type,
        is_training)
    max_update_count = len(progress_point_list)

    print(
        f'Start progress session: {participant}: {session}: {progress_type}: count = {max_update_count}')

    reset_log()
    log_events('TARGETS', time.time(), f'"{targets_string}"')
    log_events('NOISES', time.time(), f'"{noises_string}"')

    # display progress type and targets
    start_progress_data = progress_data.get_start_progress_data(progress_type, '')
    progress_data.add_eye_tracking_start(start_progress_data, participant, session)
    api_server.update_server_data(start_progress_data)
    log_events('START', time.time(), progress_type)
    # wait to update the display
    wait_progress_update(TARGETS_DISPLAY_DURATION_SECONDS / PROGRESS_DISPLAY_DURATION_SECONDS)

    # # calibration
    # api_server.update_server_data(progress_data.get_progress_data_info_point("Calibration"))
    # wait_progress_update()
    #
    # calibration_data_list = progress_data.get_progress_data_calibration()
    # update_count = 0
    # max_update_count = len(calibration_data_list)
    # next_update_time = time.time()
    #
    # print('\nCalibration START')
    # current_time = time.time()
    # log_events('CALIBRATION_START', current_time)
    # while flag_is_running and update_count < max_update_count:
    #     current_time = time.time()
    #
    #     if current_time > next_update_time:
    #         new_data = calibration_data_list[update_count]
    #         api_server.update_server_data(new_data)
    #
    #         next_update_time = current_time + PROGRESS_DISPLAY_DURATION_SECONDS
    #         update_count += 1
    #
    #     utilities.sleep_seconds(0.1)
    #     log_server_requests()
    #
    # log_events('CALIBRATION_END', current_time)
    # wait_progress_update()
    # print('Calibration STOP\n')

    # start conversation
    print('\nSTART conversation')
    start_conversation_data = progress_data.get_progress_data_info_point('Start')
    api_server.update_server_data(start_conversation_data)
    wait_progress_update()

    api_server.update_server_data(progress_data.get_empty_data())
    current_time = time.time()
    conversation_start_time = current_time
    log_events('CONVERSATION_START', current_time)

    next_update_time = current_time + PROGRESS_DISPLAY_START_DELAY_SECONDS + randint(0,
                                                                                     PROGRESS_DISPLAY_START_WAIT_RANDOM_SECONDS)

    if is_training:
        next_update_time += TRAINING_START_DELAY_SHIFT
    if is_learning:
        next_update_time = 0

    update_count = 0
    max_update_count = len(progress_point_list)
    first_time_progress_update = True

    while flag_is_running and update_count < max_update_count:
        current_time = time.time()

        if current_time > next_update_time:
            new_data = progress_point_list[update_count]
            api_server.update_server_data(new_data)
            if first_time_progress_update:
                first_time_progress_update = False
                log_events('TRIAL_START', current_time)

            next_update_time = current_time + get_next_update_gap(progress_type, is_training,
                                                                  new_data)

            if is_continuous:
                update_count += 1
            else:
                update_count += 1
                # # if current value is NOT 0 and next 2 values are 0, skip 1 value
                # if get_display_value(
                #         new_data) != 0 and update_count < max_update_count and get_display_value(
                #     progress_point_list[
                #         update_count]) == 0 and update_count + 1 < max_update_count and get_display_value(
                #     progress_point_list[update_count + 1]) == 0:
                #     update_count += 1  # is this correct?

        # utilities.sleep_seconds(0.2)
        log_server_requests()

    # wait before clearing data
    pending_requests_count = api_server.get_pending_request_count()
    print('Pending request count: ', pending_requests_count)
    wait_progress_update(pending_requests_count)
    log_events('TRIAL_END', time.time())

    # keep the 100% for PROGRESS_MAXIMUM_WAIT_IN_100_PERCENT_SECONDS
    print('\nWait in 100%: Press Esc to stop')
    wait_progress_update(
        PROGRESS_MAXIMUM_WAIT_IN_100_PERCENT_SECONDS / PROGRESS_DISPLAY_DURATION_SECONDS)

    # wait before stopping
    log_events('CONVERSATION_STOP', time.time())

    # send stop data
    print('\nSTOP conversation', progress_type)
    stop_progress_data = progress_data.get_stop_progress_data()
    progress_data.add_eye_tracking_stop(stop_progress_data, participant, session)
    api_server.update_server_data(stop_progress_data)

    log_events('STOP', time.time())
    save_log_file(participant, session)

    api_server.update_server_data(progress_data.get_empty_data())

    utilities.beep(5)
    # api_server.stop_server()


def wait_progress_update(progress_count=1):
    current_time = time.time()
    while flag_is_running and time.time() - current_time < progress_count * PROGRESS_DISPLAY_DURATION_SECONDS:
        utilities.sleep_seconds(0.1)
        log_server_requests()


def is_valid_session(session):
    if session is None or session == "":
        return False

    return -8 <= utilities.get_int(session) <= 6


def start_progress_bar_threaded(participant, session):
    threading.Thread(target=start_progress_bar, args=(participant, session)).start()


server_thread = None


def start_server_threaded():
    global server_thread
    server_thread = threading.Thread(target=api_server.start_server, daemon=True)
    server_thread.start()


def stop_server_threaded():
    global server_thread
    server_thread.join(timeout=6)


# code
listener = keyboard.Listener(on_press=on_press)
listener.start()

_participant = input("Participant (e.g., p0)?")

_session = input("Session (e.g., 1-6)?")

if is_valid_session(_session):
    start_progress_bar_threaded(_participant, _session)

api_server.start_server()
