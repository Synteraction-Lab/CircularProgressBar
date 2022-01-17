# coding=utf-8

# command format: python3 transform_progress_csv.py -p <PARTICIPANT_ID> -s <SESSION_ID>

import numpy as np
import optparse
import pandas as pd
import utilities

TESTING_SESSION_IDS = [1, 2, 3]

PROGRESS_TOLERANCE_VALUE = 0.05
PROGRESS_MAX_DIFFERENCE = 1

# input: data directory
DATA_DIRECTORY_FORMAT = 'data/{}'  # {participant}

# input: related to logged click data
FILE_NAME_CLICK_RESPONSE_FORMAT = '{}_{}_progress'

COLUMN_EVENT_TYPE = 'Event'
COLUMN_EVENT_TIME = 'Time'
COLUMN_ACTUAL_PROGRESS = 'Progress'
COLUMN_CIRCULAR_PROGRESS = 'CircularProgress'
COLUMN_LINEAR_PROGRESS = 'LinearProgress'
COLUMN_TEXT_PROGRESS = 'TextProgress'
COLUMN_PROGRESS_REQUEST_TIME = 'RequestTime'
COLUMN_EXTRA = 'Extra'

EVENT_TYPE_TARGET = 'TARGETS'
EVENT_TYPE_NOISE = 'NOISES'
EVENT_TYPE_RECEIVER = 'R'
EVENT_TYPE_OBSERVER = 'O'

# output: converted file
FILE_NAME_CONVERTED_DATA_FORMAT = 'data/{}/{}_{}_progress_converted.csv'


def read_csv_file_with_header(csv_file):
    return pd.read_csv(csv_file, header=0)


def get_targets_noises(df_event_type_column, df_event_data_column, event_type):
    target_rows = df_event_type_column[df_event_type_column == event_type].index
    targets = []
    for index in target_rows:
        if pd.notna(df_event_data_column[index]):
            targets += [int(x) for x in df_event_data_column[index].split(",")]
    targets = list(set(targets))
    targets.sort()

    return np.array(targets)


def get_value(df_column, row):
    return df_column[row]


def get_actual_progress_value(df_actual_progress_column, row):
    progress_val = get_value(df_actual_progress_column, row)
    # print(f'progress = {progress_val}')

    if pd.notna(progress_val) and progress_val != 0:
        return progress_val

    print(f'Progress values not for the row: {row}')
    return 0


def get_progress_value(df_circular_column, df_linear_column, df_text_column, row):
    circular_val = get_value(df_circular_column, row)
    linear_val = get_value(df_linear_column, row)
    text_val = get_value(df_text_column, row)

    # print(f'cir = {circular_val}, lin = {linear_val}, text = {text_val}')

    if pd.notna(circular_val) and circular_val != 0:
        return circular_val
    if pd.notna(linear_val) and linear_val != 0:
        return linear_val
    if pd.notna(text_val) and text_val != 0:
        return text_val

    print(f'Progress values not for the row: {row}')
    return 0


def get_actual_progress_update_row(progress, df_actual_progress_column, default_row):
    row_count = len(df_actual_progress_column)

    for row in range(row_count):
        progress_val = get_value(df_actual_progress_column, row)

        if pd.notna(progress_val) and progress_val >= progress:
            return row

    print(f'Progress data row not found: {progress}')
    return default_row


def get_progress_update_row(progress, df_circular_column, df_linear_column, df_text_column,
                            default_row):
    row_count = len(df_circular_column)

    for row in range(row_count):
        cir_val = get_value(df_circular_column, row)
        lin_val = get_value(df_linear_column, row)
        text_val = get_value(df_text_column, row)

        # ignore the initial values
        if cir_val == 0.5 and lin_val == 0.5:
            continue

        if (pd.notna(cir_val) and cir_val >= progress) or (
                pd.notna(lin_val) and lin_val >= progress) or (
                pd.notna(text_val) and text_val >= progress):
            return row

    print(f'Progress data row not found: {progress}')
    return default_row


def get_closest_value(value, list_values):
    if len(list_values) <= 0:
        return float('-inf')

    idx = (np.abs(list_values - value)).argmin()
    return list_values[idx]


def get_absolute(list_data):
    new_list = []
    for data in list_data:
        if pd.notna(data):
            new_list.append(abs(data))
        else:
            new_list.append(data)
    return new_list


def process_participant_session(participant, session):
    print(f'Participant: {participant}, session: {session}')
    data_directory = DATA_DIRECTORY_FORMAT.format(participant)
    # image stimuli and click data
    click_response_files = utilities.read_file_names(data_directory, '.csv',
                                                     FILE_NAME_CLICK_RESPONSE_FORMAT.format(
                                                         participant, session))
    data_frame_click_response = read_csv_file_with_header(click_response_files[0])
    # print(data_frame_click_response.shape)
    event_count = data_frame_click_response.shape[0]  # = number of events

    ori_event_type = data_frame_click_response[COLUMN_EVENT_TYPE]
    ori_event_time = np.array(data_frame_click_response[COLUMN_EVENT_TIME])
    ori_actual_progress = np.array(data_frame_click_response[COLUMN_ACTUAL_PROGRESS])
    ori_circular_progress = np.array(data_frame_click_response[COLUMN_CIRCULAR_PROGRESS])
    ori_linear_progress = np.array(data_frame_click_response[COLUMN_LINEAR_PROGRESS])
    ori_text_progress = np.array(data_frame_click_response[COLUMN_TEXT_PROGRESS])
    ori_progress_request_time = np.array(data_frame_click_response[COLUMN_PROGRESS_REQUEST_TIME])
    ori_extra = data_frame_click_response[COLUMN_EXTRA]

    # identify the targets and noises
    targets = get_targets_noises(ori_event_type, ori_extra, EVENT_TYPE_TARGET)
    noises = get_targets_noises(ori_event_type, ori_extra, EVENT_TYPE_NOISE)

    print(f'targets: {targets}, noises: {noises}')

    # receiver clicks
    receiver_rows = ori_event_type[ori_event_type == EVENT_TYPE_RECEIVER].index
    receiver_click_count = len(receiver_rows)

    # observer clicks
    observer_rows = ori_event_type[ori_event_type == EVENT_TYPE_OBSERVER].index
    observer_click_count = len(observer_rows)

    # calculate hit, miss, false alarm, reaction time, accuracy, observer_click
    hit = [None] * event_count
    miss = [None] * event_count
    false_alarm = [None] * event_count
    correct_rejection = [None] * event_count
    no_value = [None] * event_count
    reaction_time = [None] * event_count
    progress_error = [None] * event_count
    observer_click = [None] * event_count

    # add receiver clicks
    for index in receiver_rows:
        # hit or miss
        progress_val = get_actual_progress_value(ori_actual_progress, index)
        shown_progress_val = get_progress_value(ori_circular_progress, ori_linear_progress,
                                                ori_text_progress, index)
        closest_target = get_closest_value(progress_val, targets)
        closest_noise = get_closest_value(progress_val, noises)

        # print(f'progress = {progress_val}, closest_target = {closest_target}, closest_noise = {closest_noise}')

        if progress_val != shown_progress_val:
            no_value[index] = 1

        if abs(progress_val - closest_target) <= PROGRESS_TOLERANCE_VALUE:
            hit[index] = 1
            progress_error[index] = progress_val - closest_target

            # progress_update_row = get_progress_update_row(progress_val, ori_circular_progress, ori_linear_progress, ori_text_progress, index)
            progress_update_row = get_actual_progress_update_row(progress_val, ori_actual_progress,
                                                                 index)
            reaction_time[index] = get_value(ori_event_time, index) - get_value(
                ori_progress_request_time, progress_update_row)

        else:
            if abs(progress_val - closest_noise) <= PROGRESS_TOLERANCE_VALUE:
                correct_rejection[index] = 1
            elif PROGRESS_TOLERANCE_VALUE < abs(
                    progress_val - closest_noise) <= PROGRESS_MAX_DIFFERENCE:
                false_alarm[index] = 1

            # miss[index] = 1

    # add observer clicks
    for index in observer_rows:
        observer_click[index] = 1

    csv_data = {'Event': ori_event_type,
                'Time': ori_event_time,
                'Progress': ori_actual_progress,
                'CircularProgress': ori_circular_progress,
                'LinearProgress': ori_linear_progress,
                'TextProgress': ori_text_progress,
                'RequestTime': ori_progress_request_time,
                'Extra': ori_extra,
                'Hit': hit,
                'Miss': miss,
                'FalseAlarm': false_alarm,
                'CorrectRejection': correct_rejection,
                'NoValue': no_value,
                'ReactionTime': reaction_time,
                'ProgressError': progress_error,
                'ReactionTime(abs)': get_absolute(reaction_time),
                'ProgressError(abs)': get_absolute(progress_error),
                'Observer': observer_click,
                }
    # print(csv_data)
    converted_file_name = FILE_NAME_CONVERTED_DATA_FORMAT.format(participant, participant, session)
    pd.DataFrame(data=csv_data).to_csv(converted_file_name)
    print(f'\nData is written to [{converted_file_name}]')

    print_stats(receiver_click_count, observer_click_count, csv_data)


def print_stats(click_count_receiver, click_count_observer, csv_data):
    print(f'\tReceiver Clicks: {click_count_receiver}, '
          f'Observer Clicks: {click_count_observer}, '
          f'Hit: {np.sum(get_array_without_none(csv_data["Hit"]))}, '
          f'Miss: {np.sum(get_array_without_none(csv_data["Miss"]))}, '
          f'False Alarm: {np.sum(get_array_without_none(csv_data["FalseAlarm"]))}, '
          f'Correct Rejection: {np.sum(get_array_without_none(csv_data["CorrectRejection"]))}'
          f'\n')
    pass


def get_array_without_none(array):
    return [item for item in array if item is not None]


def process_participant(participant):
    for session in TESTING_SESSION_IDS:
        process_participant_session(participant, session)


parser = optparse.OptionParser()
parser.add_option("-p", "--participant", dest="participant")
parser.add_option("-s", "--session", dest="session")

options, args = parser.parse_args()

# print options
# print args
_participant = options.participant
_session = options.session

if _session is None:
    process_participant(_participant)
else:
    process_participant_session(_participant, _session)
