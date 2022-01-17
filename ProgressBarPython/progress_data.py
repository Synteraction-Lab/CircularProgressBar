# coding=utf-8

from random import sample
from random import shuffle
from random import randint

PROGRESS_DISPLAY_UPDATE_SECONDS = 3

PROGRESS_TYPE_NONE = 'none'
PROGRESS_TYPE_LINEAR_RANDOM = 'linear_random'
PROGRESS_TYPE_CIRCULAR_RANDOM = 'circular_random'
PROGRESS_TYPE_TEXT_RANDOM = 'text_random'
PROGRESS_TYPE_CIRCULAR_LEARNING = 'circular_learning'
PROGRESS_TYPE_LINEAR_LEARNING = 'linear_learning'

TARGET_VALUES_SET1 = [0.05, 0.10]
TARGET_VALUES_SET2 = [0.15, 0.20]
TARGET_VALUES_SET3 = [0.25, 0.30]
TARGET_VALUES_SET4 = [0.35, 0.40]
TARGET_VALUES_SET5 = [0.45, 0.50]
TARGET_VALUES_SET6 = [0.55, 0.60]
TARGET_VALUES_SET7 = [0.65, 0.70]
TARGET_VALUES_SET8 = [0.75, 0.80]
TARGET_VALUES_SET9 = [0.85, 0.90]
TARGET_VALUES_SET10 = [0.95, 1]

TARGET_VALUE_SET = TARGET_VALUES_SET1 \
                   + TARGET_VALUES_SET2 \
                   + TARGET_VALUES_SET3 \
                   + TARGET_VALUES_SET4 \
                   + TARGET_VALUES_SET5 \
                   + TARGET_VALUES_SET6 \
                   + TARGET_VALUES_SET7 \
                   + TARGET_VALUES_SET8 \
                   + TARGET_VALUES_SET9 \
                   + TARGET_VALUES_SET10

TRAINING_TARGET_COUNT = 5
TESTING_TARGET_COUNT = 15


# return by percentage (0-1)
def get_random_target_values(is_training):
    # choose from each set
    targets = sample(TARGET_VALUES_SET1, 1) \
              + sample(TARGET_VALUES_SET2, 1) \
              + sample(TARGET_VALUES_SET3, 1) \
              + sample(TARGET_VALUES_SET4, 1) \
              + sample(TARGET_VALUES_SET5, 1) \
              + sample(TARGET_VALUES_SET6, 1) \
              + sample(TARGET_VALUES_SET7, 1) \
              + sample(TARGET_VALUES_SET8, 1) \
              + sample(TARGET_VALUES_SET9, 1) \
              + sample(TARGET_VALUES_SET10, 1)
    # add missing from rest possible values
    targets = targets + sample(set(TARGET_VALUE_SET) - set(targets),
                               TESTING_TARGET_COUNT - len(targets))

    target_count = TESTING_TARGET_COUNT
    if is_training:
        target_count = TRAINING_TARGET_COUNT

    targets = sample(targets, target_count)

    # instead of fixed 5 increment, make it random
    for i in range(target_count):
        targets[i] = round(targets[i] - randint(0, 2) / 100, 2)

    shuffle(targets)

    shuffle_count = 0
    while get_consecutive_number_count(targets, 0.15) > 2 and shuffle_count < 20:
        shuffle(targets)
        shuffle_count += 1

    print('Targets: ', targets, ', Shuffle count: ', shuffle_count, ', Consecutive number count: ', get_consecutive_number_count(targets, 0.15))

    return targets


def get_consecutive_number_count(value_list, min_gap):
    consecutive_count = 0
    for i in range(len(value_list) - 1):
        if abs(value_list[i] - value_list[i + 1]) <= min_gap:
            consecutive_count += 1

    # print(consecutive_count)
    return consecutive_count

#
# for temp_index in range(10):
#     get_random_target_values(False)


def is_learning(progress_type):
    if progress_type == PROGRESS_TYPE_LINEAR_LEARNING or progress_type == PROGRESS_TYPE_CIRCULAR_LEARNING:
        return True
    else:
        return False


def get_empty_data():
    return {
        'progress': 0,
        'circularFill': 0,
        'circularUnfill': 0,
        'linearFill': 0,
        'linearUnfill': 0,
        'textFill': 0,
        'progressText': ''
    }


def get_start_progress_data(progress_type):
    return {
        'progress': 0,
        'circularFill': 0.5,
        'circularUnfill': 1,
        'linearFill': 0.5,
        'linearUnfill': 1,
        'textFill': 0,
        'progressText': f'{progress_type.replace("_", " ")}',
    }


def get_stop_progress_data():
    return {
        'progress': 0,
        'circularFill': 0,
        'circularUnfill': 1,
        'linearFill': 0,
        'linearUnfill': 1,
        'textFill': 0,
        'progressText': 'Stop',
    }


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


# value 0-1
def get_progress_data_linear_point(value):
    return {
        'progress': value,
        'circularFill': 0,
        'circularUnfill': 0,
        'linearFill': value,
        'linearUnfill': 1,
        'textFill': 0,
        'progressText': '',
    }


def get_progress_data_circular_point(value):
    return {
        'progress': value,
        'circularFill': value,
        'circularUnfill': 1,
        'linearFill': 0,
        'linearUnfill': 0,
        'textFill': 0,
        'progressText': '',
    }


def get_progress_data_text_point(value):
    return {
        'progress': value,
        'circularFill': 0,
        'circularUnfill': 0,
        'linearFill': 0,
        'linearUnfill': 0,
        'textFill': value,
        'progressText': '',
    }


def get_progress_data_info_point(info):
    return {
        'progress': 0,
        'circularFill': 0,
        'circularUnfill': 0,
        'linearFill': 0,
        'linearUnfill': 0,
        'textFill': 0,
        'progressText': f'{info}',
    }


def get_progress_data_calibration():
    return [
        get_progress_data_info_point('x'),
        get_progress_data_text_point(0.5),
        get_progress_data_circular_point(0.25),
        get_progress_data_circular_point(0.5),
        get_progress_data_circular_point(0.75),
        get_progress_data_linear_point(0.05),
        get_progress_data_linear_point(0.95),
        get_empty_data(),
    ]


def get_progress_learning_data(progress_type):
    if progress_type == PROGRESS_TYPE_CIRCULAR_LEARNING:
        return get_progress_data_circular_learning()
    elif progress_type == PROGRESS_TYPE_LINEAR_LEARNING:
        return get_progress_data_linear_learning()
    else:
        print(f'Unsupported type: {progress_type}')
        return []


def get_progress_testing_data(progress_type, is_training):
    if progress_type == PROGRESS_TYPE_LINEAR_RANDOM:
        return [get_progress_data_linear_point(i) for i in get_random_target_values(is_training)]
    elif progress_type == PROGRESS_TYPE_CIRCULAR_RANDOM:
        return [get_progress_data_circular_point(i) for i in get_random_target_values(is_training)]
    elif progress_type == PROGRESS_TYPE_TEXT_RANDOM:
        return [get_progress_data_text_point(i) for i in get_random_target_values(is_training)]
    elif progress_type == PROGRESS_TYPE_NONE:
        return [get_empty_data()] * len(get_random_target_values(is_training))
    else:
        print(f'Unsupported type: {progress_type}')
        return []


def get_progress_data_circular_learning():
    return [{
        'progress': i / 100,
        'circularFill': i / 100,
        'circularUnfill': 1,
        'linearFill': 0,
        'linearUnfill': 0,
        'textFill': 0,
        'progressText': f'{i}%',
    } for i in range(0, 101, 5)]


def get_progress_data_linear_learning():
    return [{
        'progress': i / 100,
        'circularFill': 0,
        'circularUnfill': 0,
        'linearFill': i / 100,
        'linearUnfill': 1,
        'textFill': 0,
        'progressText': f'{i}%',
    } for i in range(0, 101, 5)]


def add_eye_tracking_start(progress_object, participant, session):
    progress_object['config'] = f'EYE_TRACKING_START|{participant}|{session}'


def add_eye_tracking_stop(progress_object, participant, session):
    progress_object['config'] = f'EYE_TRACKING_STOP|{participant}|{session}'


def add_change_size(progress_object, linear_size, circular_size):
    progress_object['config'] = f'CHANGE_SIZE|{linear_size:.2f}|{circular_size:.2f}'


def add_change_depth(progress_object, depth):
    progress_object['config'] = f'CHANGE_DEPTH|{depth:.2f}'


def add_display_duration_millis(progress_object, display_duration_millis):
    progress_object['config'] = f'DISPLAY_DURATION|{display_duration_millis}'

# print(get_progress_learning_data(PROGRESS_TYPE_LINEAR_LEARNING), '\n')
# print(get_progress_learning_data(PROGRESS_TYPE_CIRCULAR_LEARNING), '\n')
# print(get_progress_data_calibration(), '\n')
# print(get_progress_testing_data(PROGRESS_TYPE_LINEAR_RANDOM, True), '\n')
# print(get_progress_testing_data(PROGRESS_TYPE_CIRCULAR_RANDOM, False), '\n')
# print(get_progress_testing_data(PROGRESS_TYPE_TEXT_RANDOM, False), '\n')
