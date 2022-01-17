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
import pygame_display

PROGRESS_DISPLAY_DURATION_SECONDS = 3
TRIAL_IMAGE_DISPLAY_DURATION_SECONDS = 7
TRIAL_CROSS_DISPLAY_DURATION_SECONDS = 1
TRIAL_TARGET_START_SECONDS_AFTER_IMAGE = 2
TARGET_DISPLAY_DURATION_MILLIS = 1000

flag_is_running = False

last_key = None
last_key_press_time = 0
log_queue = Queue()


def keep_key_info(key, key_time):
    global last_key, last_key_press_time
    last_key = key
    last_key_press_time = key_time


DEBOUNCE_SECONDS = 0.4  # 400 ms


def is_key_already_pressed(key, key_time):
    if key == last_key and key_time - last_key_press_time < DEBOUNCE_SECONDS:
        return True
    return False


flag_start_trial = False


def on_press(key):
    global flag_is_running, flag_start_trial
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

    if key == keyboard.Key.right:
        keep_key_info(key, current_time)
        flag_start_trial = True
        # print('start trial: ', flag_start_trial)


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


def start_progress_bar(participant, session):
    global flag_is_running

    if flag_is_running:
        print('Another instance is running')
        return

    flag_is_running = True

    # start keyboard listening
    start_keyboard_listening()
    # start api server
    start_server_threaded()
    # start display
    pygame_display.start()

    # participant session
    progress_type = participant_config.get_type(participant, session)
    is_training = utilities.get_int(session) < 0
    is_learning = progress_data.is_learning(progress_type)

    if is_learning:
        start_progress_bar_learning(participant, session, progress_type)
    else:
        start_progress_bar_testing(participant, session, progress_type, is_training)

    flag_is_running = False

    # stop display
    pygame_display.stop()
    # stop api server
    stop_server_threaded()
    # stop keyboard listening
    stop_keyboard_listening()


def start_progress_bar_learning(participant, session, progress_type):
    progress_point_list = progress_data.get_progress_learning_data(progress_type)
    max_update_count = len(progress_point_list)
    print(
        f'Start progress session: {participant}: {session}: {progress_type}: count = {max_update_count}')

    reset_log()

    # display progress type
    start_progress_data = progress_data.get_start_progress_data(progress_type)
    progress_data.add_eye_tracking_start(start_progress_data, participant, session)
    api_server.update_server_data(start_progress_data)

    current_time = time.time()
    log_events('START', current_time)

    # wait to update the display
    wait_progress_update()

    update_count = 0
    next_update_time = current_time

    while flag_is_running and update_count < max_update_count:
        current_time = time.time()

        if current_time > next_update_time:
            new_data = progress_point_list[update_count]
            api_server.update_server_data(new_data)

            next_update_time = current_time + PROGRESS_DISPLAY_DURATION_SECONDS
            update_count += 1

        utilities.sleep_seconds(0.1)
        log_server_requests()

    # wait before stopping
    wait_progress_update()

    # send stop data
    print('Stopping progress')
    stop_progress_data = progress_data.get_stop_progress_data()
    progress_data.add_eye_tracking_stop(stop_progress_data, participant, session)
    api_server.update_server_data(stop_progress_data)
    wait_progress_update()

    log_events('STOP', time.time())
    save_log_file(participant, session)

    utilities.beep(5)


def wait_progress_update(progress_count=1):
    current_time = time.time()
    while flag_is_running and time.time() - current_time < progress_count * PROGRESS_DISPLAY_DURATION_SECONDS:
        utilities.sleep_seconds(0.1)
        log_server_requests()


def get_target_string(progress_data_list):
    targets = [get_display_value(progress_obj) for progress_obj in progress_data_list]
    string_targets = [str(i) for i in targets]
    return ", ".join(string_targets)


def start_progress_bar_testing(participant, session, progress_type, is_training):
    global flag_start_trial

    calibration_data_list = progress_data.get_progress_data_calibration()
    trial_data_list = progress_data.get_progress_testing_data(progress_type, is_training)
    trial_count = len(trial_data_list)

    print(
        f'Start progress session: {participant}: {session}: {progress_type}: count = {trial_count}')

    reset_log()
    log_events('TARGETS', time.time(), f'"{get_target_string(trial_data_list)}"')

    # display progress type
    start_progress_data = progress_data.get_start_progress_data(progress_type)
    progress_data.add_eye_tracking_start(start_progress_data, participant, session)
    api_server.update_server_data(start_progress_data)

    current_time = time.time()
    log_events('START', current_time, progress_type)
    wait_progress_update()

    api_server.update_server_data(progress_data.get_progress_data_info_point("Calibration"))
    pygame_display.show_text('Calibration')
    # wait to update the display
    wait_progress_update()
    pygame_display.reset()

    update_count = 0
    max_update_count = len(calibration_data_list)
    next_update_time = current_time

    # calibration data
    print('\nCalibration START')
    current_time = time.time()
    log_events('CALIBRATION_START', current_time)
    while flag_is_running and update_count < max_update_count:
        current_time = time.time()

        if current_time > next_update_time:
            new_data = calibration_data_list[update_count]
            api_server.update_server_data(new_data)

            next_update_time = current_time + PROGRESS_DISPLAY_DURATION_SECONDS
            update_count += 1

        utilities.sleep_seconds(0.1)
        log_server_requests()

    log_events('CALIBRATION_END', current_time)
    wait_progress_update()
    print('Calibration STOP\n')

    # inform the progress type and start
    api_server.update_server_data(progress_data.get_progress_data_info_point("Starting"))
    pygame_display.show_text('Starting')
    wait_progress_update()
    api_server.update_server_data(progress_data.get_empty_data())
    pygame_display.reset()

    # trial data
    update_count = 0
    show_image_time_end = 0
    show_target_start = 0
    reset_display = False
    reset_text = True

    pygame_display.set_video()

    while flag_is_running and update_count <= trial_count:
        current_time = time.time()

        if flag_start_trial:
            flag_start_trial = False

            if update_count < trial_count:
                print(f'\nTrial: {update_count}')
                log_events('TRIAL_START', current_time)
                show_image_time_end = current_time + TRIAL_CROSS_DISPLAY_DURATION_SECONDS + TRIAL_IMAGE_DISPLAY_DURATION_SECONDS
                show_target_start = current_time + TRIAL_CROSS_DISPLAY_DURATION_SECONDS + TRIAL_TARGET_START_SECONDS_AFTER_IMAGE
            else:
                print("End of trials")
                break

        if current_time < show_image_time_end:
            if current_time < show_image_time_end - TRIAL_IMAGE_DISPLAY_DURATION_SECONDS:
                # show x
                if reset_text:
                    pygame_display.reset()
                    pygame_display.show_text('X')
                    reset_text = False
            else:
                # update image
                pygame_display.play_video()
                reset_display = True
        else:
            if reset_display:
                pygame_display.reset()
                pygame_display.show_text(f'Mark: {update_count:02d}')
                reset_display = False
                reset_text = True
                log_events('TRIAL_END', current_time)

        if show_target_start != 0 and current_time > show_target_start:
            new_data = trial_data_list[update_count]
            progress_data.add_display_duration_millis(new_data, TARGET_DISPLAY_DURATION_MILLIS)
            api_server.update_server_data(new_data)
            print(f'Update target: {get_display_value(new_data)}')

            # clear it later
            api_server.update_server_data(progress_data.get_empty_data())
            update_count += 1

            show_target_start = 0

        utilities.sleep_milliseconds(5)
        log_server_requests()

    pygame_display.reset_video()

    pygame_display.reset()
    pygame_display.show_text('Fill questionnaire')
    # send stop data
    print('\nStopping progress')
    stop_progress_data = progress_data.get_stop_progress_data()
    progress_data.add_eye_tracking_stop(stop_progress_data, participant, session)
    api_server.update_server_data(stop_progress_data)
    wait_progress_update()

    api_server.update_server_data(progress_data.get_empty_data())

    log_events('STOP', time.time())
    save_log_file(participant, session)

    utilities.beep(5)


def is_valid_session(session):
    if session is None or session == "":
        return False

    return -8 <= utilities.get_int(session) <= 6


def start_progress_bar_with_exception(participant, session):
    try:
        start_progress_bar(participant, session)
    except Exception:
        print("Unhandled exception")
        traceback.print_exc(file=sys.stdout)


def start_progress_bar_threaded(participant, session):
    threading.Thread(target=start_progress_bar_with_exception,
                     args=(participant, session)).start()


def cancel_progress_bar():
    global flag_is_running
    print('Cancel progress')
    flag_is_running = False


server_thread = None


def start_server_threaded():
    global server_thread
    server_thread = threading.Thread(target=api_server.start_server, daemon=True)
    server_thread.start()


def stop_server_threaded():
    global server_thread
    server_thread.join(timeout=4)


keyboard_listener = None


def start_keyboard_listening():
    global keyboard_listener
    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()


def stop_keyboard_listening():
    global keyboard_listener
    keyboard_listener.stop()
    # pass


# code

_participant = input("Participant (e.g., p0)?")
_session = input("Session (e.g., 1-3)?")

if is_valid_session(_session):
    start_progress_bar(_participant, _session)
