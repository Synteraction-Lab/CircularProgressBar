# coding=utf-8

# command format: python3 transform_eye_gaze_csv.py -p <PARTICIPANT_ID> -s <SESSION_ID> -v <0/1>

import numpy as np
import math
import optparse
import pandas as pd
import utilities
import matplot_plot

TESTING_SESSION_IDS = [1, 2, 3, 4, 5, 6]

# input: data directory
DATA_DIRECTORY_FORMAT = 'data/{}'  # {participant}

# input: related to logged progress data
FILE_NAME_STIMULI_RESPONSE_FORMAT = '{}_{}_progress'

COLUMN_EVENT_TYPE = 'Event'
COLUMN_EVENT_TIME = 'Time'
COLUMN_ACTUAL_PROGRESS = 'Progress'
COLUMN_CIRCULAR_PROGRESS = 'CircularProgress'
COLUMN_LINEAR_PROGRESS = 'LinearProgress'
COLUMN_TEXT_PROGRESS = 'TextProgress'
COLUMN_PROGRESS_REQUEST_TIME = 'RequestTime'
COLUMN_EXTRA = 'Extra'

EVENT_TYPE_TARGETS = 'TARGETS'
EVENT_TYPE_CALIBRATION = 'CALIBRATION_'  # start or end
EVENT_TYPE_CALIBRATION_START = 'CALIBRATION_START'
EVENT_TYPE_CALIBRATION_END = 'CALIBRATION_END'
EVENT_TYPE_TRIAL = 'TRIAL_'  # start or end
EVENT_TYPE_TRIAL_START = 'TRIAL_START'
EVENT_TYPE_TRIAL_END = 'TRIAL_END'
EVENT_TYPE_DATA_REQUEST = 'SERVER_REQUEST'

EVENT_DATA_EYE_TRACKING = 'EYE_TRACKING_'
EVENT_DATA_EYE_TRACKING_START = 'EYE_TRACKING_START'
EVENT_DATA_EYE_TRACKING_STOP = 'EYE_TRACKING_STOP'

# input: related to eye tracking data
FILE_NAME_EYE_TRACKING_FORMAT = '{}_{}_eyes'

COLUMN_EYE_USER_ID = 'UserId'
COLUMN_EYE_SESSION = ' SessionType'
COLUMN_EYE_TIME = ' dt in ms'
COLUMN_EYE_DIR_X = ' EyeDir.x'
COLUMN_EYE_DIR_Y = ' EyeDir.y'
COLUMN_EYE_DIR_Z = ' EyeDir.z'

# output: converted file
FILE_NAME_CONVERTED_DATA_FORMAT = 'data/{}/{}_{}_eye_tracking_converted.csv'
FILE_NAME_CONVERTED_SUMMARY_DATA_FORMAT = 'data/{}/{}_{}_eye_tracking_summary.csv'


def read_csv_file_with_header(csv_file):
    return pd.read_csv(csv_file, header=0)


def get_event_start_with_rows(df_event_type_column, event_type):
    return df_event_type_column[df_event_type_column.str.startswith(event_type, na=False)].index


def get_targets_noises(df_event_type_column, df_event_data_column, event_type):
    target_rows = get_event_start_with_rows(df_event_type_column, event_type)
    # print(target_rows)
    targets = []
    for index in target_rows:
        if pd.notna(df_event_data_column[index]):
            targets += [float(x) for x in df_event_data_column[index].split(",")]

    return np.array(targets)


def get_rows_between(df_column, start_val, end_val):
    return df_column[df_column.between(start_val, end_val)].index


def get_value(df_column, row):
    return df_column[row]


def process_participant_session(participant, session, visualize=False):
    print(f'Participant: {participant}, session: {session}')
    data_directory = DATA_DIRECTORY_FORMAT.format(participant)

    # image stimuli data
    stimuli_data_files = utilities.read_file_names(data_directory, '.csv',
                                                   FILE_NAME_STIMULI_RESPONSE_FORMAT.format(
                                                       participant, session))
    data_frame_stimuli_response = read_csv_file_with_header(stimuli_data_files[0])
    # print(data_frame_stimuli_response.shape)

    ori_event_type = data_frame_stimuli_response[COLUMN_EVENT_TYPE]
    ori_event_time = np.array(data_frame_stimuli_response[COLUMN_EVENT_TIME])
    ori_progress_request_time = np.array(data_frame_stimuli_response[COLUMN_PROGRESS_REQUEST_TIME])
    ori_event_extra = data_frame_stimuli_response[COLUMN_EXTRA]

    # eye tracking data
    eye_tracking_data_files = utilities.read_file_names(data_directory, '.csv',
                                                        FILE_NAME_EYE_TRACKING_FORMAT.format(
                                                            participant, session))
    data_frame_eye_tracking = read_csv_file_with_header(eye_tracking_data_files[0])
    # print(data_frame_eye_tracking.shape)

    ori_eye_tracking_time = data_frame_eye_tracking[COLUMN_EYE_TIME]

    # identify the targets and noises
    targets = get_targets_noises(ori_event_type, ori_event_extra, EVENT_TYPE_TARGETS)
    print(f'targets: {targets}')

    # stimuli file rows: eye_tracking, calibrations, trials, display_duration
    event_eye_tracking_start_rows = get_event_start_with_rows(ori_event_extra,
                                                              EVENT_DATA_EYE_TRACKING_START)
    event_calibration_rows = get_event_start_with_rows(ori_event_type, EVENT_TYPE_CALIBRATION)
    event_trial_rows = get_event_start_with_rows(ori_event_type, EVENT_TYPE_TRIAL)

    if len(event_trial_rows) % 2 != 0:
        print(f'Error in trial row count: {len(event_trial_rows)}')
        return

    trial_count = len(event_trial_rows) // 2

    print(
        f'Calibration rows: {len(event_calibration_rows)}, Trial rows: {len(event_trial_rows)}, Trial count: {trial_count}')

    # eye tracking start time (in seconds) w.r.t. stimuli file -> corresponds to 0 (milli seconds) in eye tracking file
    stimuli_eye_tracking_start_time = get_value(ori_progress_request_time,
                                                event_eye_tracking_start_rows[0])

    # eye-tracking file rows:
    # print(event_calibration_rows)
    calibration_start_millis = (get_value(ori_progress_request_time, event_calibration_rows[
        0]) - stimuli_eye_tracking_start_time) * 1000
    calibration_end_millis = (get_value(ori_progress_request_time, event_calibration_rows[
        1]) - stimuli_eye_tracking_start_time) * 1000
    eye_tracking_calibration_rows = get_rows_between(ori_eye_tracking_time
                                                     , calibration_start_millis
                                                     , calibration_end_millis)

    new_column_trial_info = ['C'] * len(eye_tracking_calibration_rows)

    # eye-tracking trial data
    eye_tracking_trial_rows = []
    for trial in range(trial_count):
        eye_tracking_trial_rows.append([])
        trial_start_millis = (get_value(ori_progress_request_time, event_trial_rows[
            2 * trial]) - stimuli_eye_tracking_start_time) * 1000
        trial_end_millis = (get_value(ori_event_time, event_trial_rows[
            2 * trial + 1]) - stimuli_eye_tracking_start_time) * 1000
        eye_tracking_trial_rows[trial] = get_rows_between(ori_eye_tracking_time, trial_start_millis,
                                                          trial_end_millis)
        new_column_trial_info += [trial] * len(eye_tracking_trial_rows[trial])

    # concat all selected rows
    filtered_eye_tracking_rows = np.array(eye_tracking_calibration_rows)
    for i in range(len(eye_tracking_trial_rows)):
        filtered_eye_tracking_rows = np.concatenate(
            (filtered_eye_tracking_rows, eye_tracking_trial_rows[i]))

    # print(len(filtered_eye_tracking_rows), len(new_column_trial_info))
    data_frame_eye_tracking_trials_filtered = data_frame_eye_tracking.loc[
        filtered_eye_tracking_rows]
    data_frame_eye_tracking_trials_filtered['TrialInfo'] = new_column_trial_info
    # print(data_frame_eye_tracking_trials_filtered)

    converted_file_name = FILE_NAME_CONVERTED_DATA_FORMAT.format(participant, participant, session)
    pd.DataFrame(data=data_frame_eye_tracking_trials_filtered).to_csv(converted_file_name)
    print(f'\nData is written to [{converted_file_name}]')

    # summary data related to [calibration, trial 0, trial 1, ...]
    calibration_trial_rows = get_calibration_trial_rows(eye_tracking_calibration_rows,
                                                        eye_tracking_trial_rows)
    trial_info = ['C'] + [i for i in
                          range(trial_count)]  # Add 'C' for calibration and 0-n for trials
    eye_gaze_x, eye_gaze_y, eye_gaze_z, eye_gaze_t = get_eye_gaze_xyzt(data_frame_eye_tracking,
                                                                       calibration_trial_rows)
    eye_gaze_dir_x_mean, eye_gaze_dir_x_std, eye_gaze_dir_y_mean, eye_gaze_dir_y_std, eye_gaze_dir_z_mean, eye_gaze_dir_z_std, eye_gaze_duration = get_eye_gaze_mean_std_xyz_t(
        eye_gaze_x, eye_gaze_y, eye_gaze_z, eye_gaze_t)

    calibration_center_point, calibration_radius = get_calibration_canter_and_radius(participant,
                                                                                     session,
                                                                                     eye_gaze_x[0],
                                                                                     eye_gaze_y[0],
                                                                                     eye_gaze_z[0])
    print('Center:', calibration_center_point, ', Radius: :', calibration_radius)
    eye_gaze_within_radius_percentages = get_eye_gaze_within_radius(eye_gaze_x, eye_gaze_y,
                                                                    eye_gaze_z,
                                                                    calibration_center_point,
                                                                    calibration_radius)
    csv_summary_data = {
        'TrialInfo': trial_info,
        'EyeDir.x.mean': eye_gaze_dir_x_mean,
        'EyeDir.x.std': eye_gaze_dir_x_std,
        'EyeDir.y.mean': eye_gaze_dir_y_mean,
        'EyeDir.y.std': eye_gaze_dir_y_std,
        'EyeDir.z.mean': eye_gaze_dir_z_mean,
        'EyeDir.z.std': eye_gaze_dir_z_std,
        'EyeDir.duration': eye_gaze_duration,
        'Gaze.count.percentage': eye_gaze_within_radius_percentages,
    }
    # print(csv_summary_data)
    converted_summary_file_name = FILE_NAME_CONVERTED_SUMMARY_DATA_FORMAT.format(participant,
                                                                                 participant,
                                                                                 session)
    pd.DataFrame(data=csv_summary_data).to_csv(converted_summary_file_name)
    print(f'\nData is written to [{converted_summary_file_name}]')

    print_stats(csv_summary_data)

    if visualize:
        visualize_eye_gaze(eye_gaze_x, eye_gaze_y, eye_gaze_z)


def get_calibration_canter_and_radius(participant, session, calibration_eye_gaze_x,
                                      calibration_eye_gaze_y, calibration_eye_gaze_z):
    # get 2 points from calibration data
    calibration_points = matplot_plot.get_selected_points_manually(
        f'data/{participant}/{participant}_{session}_calibration', ['C', 'R'],
        calibration_eye_gaze_x,
        calibration_eye_gaze_y, calibration_eye_gaze_z)
    # print(calibration_points)
    calibration_center_point = calibration_points[0]
    calibration_radius_point = calibration_points[1]
    calibration_radius = math.sqrt(
        (calibration_radius_point[0] - calibration_center_point[0]) ** 2 + (
                calibration_radius_point[1] - calibration_center_point[1]) ** 2)
    return calibration_center_point, calibration_radius


# return [[<calibration>], [<trial 0>], ...]
def get_calibration_trial_rows(calibration_rows, trial_rows):
    calibration_trial_rows = [[]]
    # add calibration gaze data as 0 index
    calibration_trial_rows[0] = calibration_rows
    for i in range(len(trial_rows)):
        calibration_trial_rows.append(trial_rows[i])

    return calibration_trial_rows


# return x:[[]], y:[[]], z:[[]], t:[[]]
def get_eye_gaze_xyzt(eye_tracking_data_frame, calibration_trial_rows):
    eye_gaze_x = []
    eye_gaze_y = []
    eye_gaze_z = []
    eye_gaze_t = []
    total_rows = len(calibration_trial_rows)
    for i in range(total_rows):
        df_trial_data = eye_tracking_data_frame.loc[calibration_trial_rows[i]]
        eye_gaze_x.append(np.array(df_trial_data[COLUMN_EYE_DIR_X]))
        eye_gaze_y.append(np.array(df_trial_data[COLUMN_EYE_DIR_Y]))
        eye_gaze_z.append(np.array(df_trial_data[COLUMN_EYE_DIR_Z]))
        eye_gaze_t.append(np.array(df_trial_data[COLUMN_EYE_TIME]))

    return eye_gaze_x, eye_gaze_y, eye_gaze_z, eye_gaze_t


# eye_gaze_x = [[]]
def get_eye_gaze_mean_std_xyz_t(eye_gaze_x, eye_gaze_y, eye_gaze_z, eye_gaze_t):
    eye_gaze_dir_x_mean = []
    eye_gaze_dir_x_std = []
    eye_gaze_dir_y_mean = []
    eye_gaze_dir_y_std = []
    eye_gaze_dir_z_mean = []
    eye_gaze_dir_z_std = []
    eye_gaze_duration = []

    bin_count = len(eye_gaze_x)

    for i in range(bin_count):
        eye_gaze_dir_x_mean.append(np.mean(eye_gaze_x[i], axis=0))
        eye_gaze_dir_x_std.append(np.std(eye_gaze_x[i], axis=0))
        eye_gaze_dir_y_mean.append(np.mean(eye_gaze_y[i], axis=0))
        eye_gaze_dir_y_std.append(np.std(eye_gaze_y[i], axis=0))
        eye_gaze_dir_z_mean.append(np.mean(eye_gaze_z[i], axis=0))
        eye_gaze_dir_z_std.append(np.std(eye_gaze_z[i], axis=0))
        eye_gaze_duration.append(eye_gaze_t[i][-1] - eye_gaze_t[i][0])

    return eye_gaze_dir_x_mean, eye_gaze_dir_x_std, eye_gaze_dir_y_mean, eye_gaze_dir_y_std, eye_gaze_dir_z_mean, eye_gaze_dir_z_std, eye_gaze_duration


# input: eye_gaze_x:[[]], ..., region_center = [x, y, z], region_radius = r
# return [percentage 0, percentage 1, ...]
def get_eye_gaze_within_radius(eye_gaze_x, eye_gaze_y, eye_gaze_z, region_center, region_radius):
    bin_count = len(eye_gaze_x)
    eye_gaze_percentage = []

    for i in range(bin_count):
        eye_gaze_percentage.append(get_percentage_within_region(eye_gaze_x[i], eye_gaze_y[i],
                                                                eye_gaze_z[i], region_center,
                                                                region_radius))

    return eye_gaze_percentage


# input: eye_gaze_x = [], .., region_center = (x, y, z), region_radius = r
def get_percentage_within_region(eye_gaze_x, eye_gaze_y, eye_gaze_z, region_center, region_radius):
    row_count = len(eye_gaze_x)
    center_x = region_center[0]
    center_y = region_center[1]
    radius2 = region_radius ** 2

    within_radius_count = 0

    for i in range(row_count):
        x = eye_gaze_x[i]
        y = eye_gaze_y[i]
        if ((x - center_x) ** 2 + (y - center_y) ** 2) <= radius2:
            within_radius_count += 1

    return within_radius_count / row_count


def print_stats(eye_tacking_summary_data):
    print('Gaze.count.percentage: ', eye_tacking_summary_data['Gaze.count.percentage'])


def visualize_eye_gaze(eye_gaze_x, eye_gaze_y, eye_gaze_z):
    fig_count = len(eye_gaze_x)

    # assume 0 is the calibration data and fix the range
    # mean_x = np.mean(eye_gaze_x[0], axis=0)
    # std_x = np.std(eye_gaze_x[0], axis=0)
    # mean_y = np.mean(eye_gaze_y[0], axis=0)
    # std_y = np.std(eye_gaze_y[0], axis=0)
    # z_min = np.amin(eye_gaze_z[0], axis=0)
    # z_max = np.amax(eye_gaze_z[0], axis=0)
    #
    # matplot_plot.fix_visualize_range(
    #     [mean_x - 3  * std_x, mean_x + 3 * std_x,
    #      mean_y - 3 * std_y,  mean_y - 2.5 * std_y,
    #      z_min, z_max])

    for i in range(fig_count):
        matplot_plot.new_figure()
        matplot_plot.visualize_data_3d(eye_gaze_x[i], eye_gaze_y[i], eye_gaze_z[i])
        matplot_plot.display_figure(f'Trial: {i}')


def get_array_without_none(array):
    return [item for item in array if item is not None]


def process_participant(participant):
    for session in TESTING_SESSION_IDS:
        process_participant_session(participant, session)


parser = optparse.OptionParser()
parser.add_option("-p", "--participant", dest="participant")
parser.add_option("-s", "--session", dest="session")
parser.add_option("-v", "--visualize", dest="visualize")

options, args = parser.parse_args()

# print options
# print args
_participant = options.participant
_session = options.session
_visualize = options.visualize

if _session is None:
    process_participant(_participant)
else:
    process_participant_session(_participant, _session, _visualize == '1')
