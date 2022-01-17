# coding=utf-8

from random import sample

PROGRESS_DISPLAY_UPDATE_SECONDS = 3
PROGRESS_DISPLAY_DATA_PRECISION = 1  # 2 deg
PROGRESS_DISPLAY_DATA_POINTS = 100 // PROGRESS_DISPLAY_DATA_PRECISION
PROGRESS_DISPLAY_DURATION_SECONDS = PROGRESS_DISPLAY_DATA_POINTS * PROGRESS_DISPLAY_UPDATE_SECONDS
print(f'PROGRESS_DISPLAY_DURATION_SECONDS: {PROGRESS_DISPLAY_DURATION_SECONDS}')

PROGRESS_TYPE_NONE = 'none'
PROGRESS_TYPE_LINEAR_CONTINUOUS = 'linear_continuous'
PROGRESS_TYPE_LINEAR_INTERMITTENT = 'linear_intermittent'
PROGRESS_TYPE_CIRCULAR_CONTINUOUS = 'circular_continuous'
PROGRESS_TYPE_CIRCULAR_INTERMITTENT = 'circular_intermittent'
PROGRESS_TYPE_TEXT_CONTINUOUS = 'text_continuous'
PROGRESS_TYPE_TEXT_INTERMITTENT = 'text_intermittent'
PROGRESS_TYPE_CIRCULAR_LEARNING = 'circular_learning'
PROGRESS_TYPE_LINEAR_LEARNING = 'linear_learning'


# return by percentage (0-100)
def get_target_noise_values():
    targets = list(range(10, 101, 10))
    noises = []

    print('Targets: ', targets)
    print('Noises: ', noises)

    return targets, noises


# get_target_noise_values()

def is_learning(progress_type):
    if progress_type == PROGRESS_TYPE_LINEAR_LEARNING or progress_type == PROGRESS_TYPE_CIRCULAR_LEARNING:
        return True
    else:
        return False


def is_continuous(progress_type):
    if progress_type == PROGRESS_TYPE_LINEAR_CONTINUOUS or progress_type == PROGRESS_TYPE_CIRCULAR_CONTINUOUS or progress_type == PROGRESS_TYPE_TEXT_CONTINUOUS:
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


def get_start_progress_data(progress_type, targets=''):
    return {
        'progress': 0,
        'circularFill': 0.5,
        'circularUnfill': 1,
        'linearFill': 0.5,
        'linearUnfill': 1,
        'textFill': 0,
        'progressText': f'{progress_type.replace("_", " ")}\n{targets}',
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


# return the targets_string, noises_string, progress_data_points
def get_progress_data(progress_type, training=False):
    if progress_type == PROGRESS_TYPE_NONE:
        return '', '', get_progress_data_none()
    elif progress_type == PROGRESS_TYPE_CIRCULAR_LEARNING:
        return '', '', get_progress_data_circular_learning()
    elif progress_type == PROGRESS_TYPE_LINEAR_LEARNING:
        return '', '', get_progress_data_linear_learning()

    targets, noises = get_target_noise_values()
    targets_string = get_target_string(targets)
    noises_string = get_target_string(noises)

    if progress_type == PROGRESS_TYPE_LINEAR_CONTINUOUS:
        return targets_string, noises_string, get_progress_data_linear_continuous(training)
    elif progress_type == PROGRESS_TYPE_LINEAR_INTERMITTENT:
        return targets_string, noises_string, get_progress_data_linear_intermittent(targets, noises,
                                                                                    training)
    elif progress_type == PROGRESS_TYPE_CIRCULAR_CONTINUOUS:
        return targets_string, noises_string, get_progress_data_circular_continuous(training)
    elif progress_type == PROGRESS_TYPE_CIRCULAR_INTERMITTENT:
        return targets_string, noises_string, get_progress_data_circular_intermittent(targets,
                                                                                      noises,
                                                                                      training)
    elif progress_type == PROGRESS_TYPE_TEXT_CONTINUOUS:
        return targets_string, noises_string, get_progress_data_text_continuous(training)
    elif progress_type == PROGRESS_TYPE_TEXT_INTERMITTENT:
        return targets_string, noises_string, get_progress_data_text_intermittent(targets,
                                                                                  noises,
                                                                                  training)
    else:
        print(f'Unsupported type: {progress_type}')
        return '', '', get_progress_data_none()


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


def get_target_string(targets=[]):
    string_targets = [str(i) for i in targets]
    return ", ".join(string_targets)


def get_progress_string(value, is_training):
    # if is_training:
    #     return f'{value * 100:.0f}%'
    return ''


# return values in 0.00-1.00
def get_continuous_data(training):
    if training:
        continuous_data_point_count = PROGRESS_DISPLAY_DATA_POINTS // 4
    else:
        continuous_data_point_count = PROGRESS_DISPLAY_DATA_POINTS
    return [(i / continuous_data_point_count) for i in range(1, continuous_data_point_count + 1)]


# return values in 0.00-1.00
def get_intermittent_data(targets, noises, training):
    # targets and noises in 0-100
    display_items = targets + noises
    display_items.sort()

    # in 0.0-1.0
    intermittent_data_points = get_continuous_data(training)

    # set 0 to all items that are not close to targets or noises
    display_item_index = 0
    for current_item in range(len(intermittent_data_points)):
        if display_item_index < len(display_items):
            if intermittent_data_points[current_item] < (display_items[display_item_index] / 100):
                intermittent_data_points[current_item] = 0
            else:
                display_item_index += 1
        else:
            intermittent_data_points[current_item] = 0

    # print(intermittent_data_points)
    return intermittent_data_points


# for _i in range(10):
#     _targets, _noises = get_target_noise_values()
#     get_intermittent_data(_targets, _noises)


def get_progress_data_none():
    return [get_empty_data()] * PROGRESS_DISPLAY_DATA_POINTS


def get_progress_data_linear_continuous(training):
    return [{
        'progress': i,
        'circularFill': 0,
        'circularUnfill': 0,
        'linearFill': i,
        'linearUnfill': 1,
        'textFill': 0,
        'progressText': get_progress_string(i, training),
    } for i in get_continuous_data(training)]


def get_progress_data_linear_intermittent(targets, noises, training):
    intermittent_data = get_intermittent_data(targets, noises, training)
    continuous_data = get_continuous_data(training)
    return [{
        'progress': continuous_data[index],
        'circularFill': 0,
        'circularUnfill': 0,
        'linearFill': intermittent_data[index],
        'linearUnfill': 1 if intermittent_data[index] != 0 else 0,
        'textFill': 0,
        'progressText': '' if intermittent_data[index] == 0 else get_progress_string(
            intermittent_data[index], training),
    } for index in range(len(intermittent_data))]


def get_progress_data_circular_continuous(training):
    return [{
        'progress': i,
        'circularFill': i,
        'circularUnfill': 1,
        'linearFill': 0,
        'linearUnfill': 0,
        'textFill': 0,
        'progressText': get_progress_string(i, training),
    } for i in get_continuous_data(training)]


def get_progress_data_circular_intermittent(targets, noises, training):
    intermittent_data = get_intermittent_data(targets, noises, training)
    continuous_data = get_continuous_data(training)
    return [{
        'progress': continuous_data[index],
        'circularFill': intermittent_data[index],
        'circularUnfill': 1 if intermittent_data[index] != 0 else 0,
        'linearFill': 0,
        'linearUnfill': 0,
        'textFill': 0,
        'progressText': '' if intermittent_data[index] == 0 else get_progress_string(
            intermittent_data[index], training),
    } for index in range(len(intermittent_data))]


def get_progress_data_text_continuous(training):
    return [{
        'progress': i,
        'circularFill': 0,
        'circularUnfill': 0,
        'linearFill': 0,
        'linearUnfill': 0,
        'textFill': i,
        'progressText': get_progress_string(i, training),
    } for i in get_continuous_data(training)]


def get_progress_data_text_intermittent(targets, noises, training):
    intermittent_data = get_intermittent_data(targets, noises, training)
    continuous_data = get_continuous_data(training)
    return [{
        'progress': continuous_data[index],
        'circularFill': 0,
        'circularUnfill': 0,
        'linearFill': 0,
        'linearUnfill': 0,
        'textFill': intermittent_data[index],
        'progressText': '' if intermittent_data[index] == 0 else get_progress_string(
            intermittent_data[index], training),
    } for index in range(len(intermittent_data))]


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
        # get_progress_data_info_point('Calibration'),
        get_progress_data_info_point('x'),
        get_progress_data_text_point(0.5),
        # get_progress_data_circular_point(0.25),
        get_progress_data_circular_point(0.5),
        # get_progress_data_circular_point(0.75),
        # get_progress_data_linear_point(0.05),
        # get_progress_data_linear_point(0.95),
        # get_empty_data(),
    ]

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

# print(get_progress_data(PROGRESS_TYPE_NONE, True), '\n')
# print(get_progress_data(PROGRESS_TYPE_LINEAR_CONTINUOUS, True), '\n')
# print(get_progress_data(PROGRESS_TYPE_LINEAR_INTERMITTENT, False), '\n')
# print(get_progress_data(PROGRESS_TYPE_CIRCULAR_CONTINUOUS, False), '\n')
# print(get_progress_data(PROGRESS_TYPE_CIRCULAR_INTERMITTENT, True), '\n')
# print(get_progress_data(PROGRESS_TYPE_TEXT_CONTINUOUS, False), '\n')
# print(get_progress_data(PROGRESS_TYPE_TEXT_INTERMITTENT, True), '\n')
# print(get_progress_data(PROGRESS_TYPE_CIRCULAR_LEARNING, True), '\n')
# print(get_progress_data(PROGRESS_TYPE_LINEAR_LEARNING, True), '\n')
