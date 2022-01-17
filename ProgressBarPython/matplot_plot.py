# coding=utf-8

import sys
import numpy as np
import matplotlib.pyplot as plt



ENABLE_ANNOTATION = False

fix_x_min = None
fix_x_max = None
fix_y_min = None
fix_y_max = None
fix_z_min = None
fix_z_max = None


# xyz_min_max = [x_min, x_max, y_min, y_max, z_min, z_max]
def fix_visualize_range(xyz_min_max):
    global fix_x_min, fix_x_max, fix_y_min, fix_y_max, fix_z_min, fix_z_max

    if len(xyz_min_max) != 6:
        print('Error in parameter')
    else:
        fix_x_min = xyz_min_max[0]
        fix_x_max = xyz_min_max[1]
        fix_y_min = xyz_min_max[2]
        fix_y_max = xyz_min_max[3]
        fix_z_min = xyz_min_max[4]
        fix_z_max = xyz_min_max[5]


# return [x_min, x_max, y_min, y_max, z_min, z_max]
def get_visualize_range(x, y, z):
    if fix_x_min is not None:
        return [fix_x_min, fix_x_max, fix_y_min, fix_y_max, fix_z_min, fix_z_max]

    mean_x = np.mean(x, axis=0)
    std_x = np.std(x, axis=0)
    mean_y = np.mean(y, axis=0)
    std_y = np.std(y, axis=0)
    x_min = np.amin(x, axis=0)
    x_max = np.amax(x, axis=0)
    y_min = np.amin(y, axis=0)
    y_max = np.amax(y, axis=0)
    z_min = np.amin(z, axis=0)
    z_max = np.amax(z, axis=0)

    # print(mean_x, mean_y)

    return [x_min, x_max,
            y_min, y_max,
            z_min, z_max]


def visualize_data_2d(x, y, t, gap=0, line=False):
    # plt.figure()

    ax = plt.gca()
    ax.grid()

    [x_min, x_max, y_min, y_max, t_min, t_max] = get_visualize_range(x, y, t)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    ax.set_xlabel('x')
    ax.set_ylabel('y')

    # add annotations if enabled
    if ENABLE_ANNOTATION:
        for i in range(len(x)):
            ax.annotate(f'{i}', (x[i], y[i]), color='c')

    # annotations
    annotations = []
    for i in range(len(x)):
        ann_ = ax.annotate(f'{t[i]:.3f}', (x[i], y[i]), color='r', visible=False)
        setattr(ann_, 'time', t[i])
        setattr(ann_, 'index', i)
        annotations.append(ann_)
    annotations[0].set_visible(True)
    annotations[len(annotations) - 1].set_visible(True)

    # support for annotation showing with mouse clicks
    fig = plt.gcf()
    fig.canvas.mpl_connect('button_press_event',
                           lambda event: show_nearby_annotations(fig, [event.xdata, event.ydata],
                                                                 annotations))

    # plotting
    if line:
        plot_line(ax, x, y, gap)
    else:
        plot_scatter(ax, x, y, gap)

    update_figure(fig)


def new_figure():
    return plt.figure()


def update_figure(figure):
    figure.canvas.draw()


def close_figure(figure):
    plt.close(figure)


def display_figure(title=None, tight=True):
    if title is not None:
        fig = plt.gcf()
        set_title(fig, title)

    if tight:
        plt.tight_layout()
    plt.show()


def save_figure(filename, figure=None):
    if figure is None:
        # plt.tight_layout()
        figure = plt.gcf()
        set_title(figure, filename)

    figure.savefig(f'{filename}.png', dpi=300, bbox_inches='tight', pad_inches=0.1,
                   transparent=False)
    print(f'saving figure: [{filename}.png]')


def set_title(figure, title):
    axes = figure.get_axes()
    for ax in axes:
        ax.set_title(title)


def maximize_figure():
    fig_manager = plt.get_current_fig_manager()
    if sys.platform.find('linux') != -1:
        fig_manager.window.showMaximized()
    elif sys.platform.find('win') != -1:
        fig_manager.window.state('zoomed')
    else:
        fig_manager.frame.Maximize(True)


def plot_scatter(axis, x, y, gap):
    if isinstance(gap, list):
        for i in range(len(x)):
            axis.scatter(x[i], y[i], zorder=2)
            plt.pause(gap[i])
    else:
        if gap == 0:
            axis.scatter(x, y, zorder=2)
        elif gap > 0:
            for i in range(len(x)):
                axis.scatter(x[i], y[i], zorder=2)
                plt.pause(gap)
        else:
            raise TypeError(f'Unsupported gap: {gap}')
    print('Completed drawing')


def plot_line(axis, x, y, gap, marker='yo-'):
    if isinstance(gap, list):
        for i in range(1, len(x)):
            axis.plot([x[i - 1], x[i]], [y[i - 1], y[i]], marker, zorder=2)
            plt.pause(gap[i])
    else:
        if gap == 0:
            axis.plot(x, y, marker, zorder=2)
        elif gap > 0:
            for i in range(1, len(x)):
                axis.plot([x[i - 1], x[i]], [y[i - 1], y[i]], marker, zorder=2)
                plt.pause(gap)
        else:
            raise TypeError(f'Unsupported gap: {gap}')
    print('Completed drawing')


# xy = (x, y)
def is_close_annotation(xy, annotation):
    if len(xy) != 2 or xy[0] is None or xy[1] is None:
        return False

    tolerance = 4
    return xy[0] - tolerance < annotation.xy[0] < xy[0] + tolerance and \
           xy[1] - tolerance < annotation.xy[1] < xy[1] + tolerance


def show_nearby_annotations(figure, xy, annotations):
    # print(mouse_event)
    nearby_annotations = [annotation for annotation in annotations if
                          is_close_annotation(xy, annotation)]

    if len(nearby_annotations) > 0:
        print('Annotations near ', xy)
    for ann in nearby_annotations:
        ann.set_visible(True)
        print(
            f'\t Annotation - index:{ann.index} , time: {ann.time: .3f} , ({ann.xy[0]:.3f}, {ann.xy[1]:.3f})')
    if len(nearby_annotations) > 0:
        update_figure(figure)


def visualize_data_3d(x, y, z, gap=0):
    plt.grid()

    ax = plt.axes(projection='3d')
    # ax.view_init(azim=-60, elev=30)
    ax.view_init(azim=-90, elev=90)
    # fig = plt.figure()
    # ax = Axes3D(fig, azim=-90, elev=90)

    [x_min, x_max, y_min, y_max, z_min, z_max] = get_visualize_range(x, y, z)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(z_min, z_max)

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    if isinstance(gap, list):
        for i in range(len(x)):
            ax.scatter(x[i], y[i], z[i], zorder=2)
            plt.pause(gap[i])
    else:
        if gap == 0:
            ax.scatter(x, y, z, zorder=2, s = 30)
        if gap > 0:
            for i in range(len(x)):
                ax.scatter(x[i], y[i], z[i], zorder=2)
                plt.pause(gap)

    print('Completed drawing')




_temp_marker_index = 0
_temp_calibration_mapping = [] # keep points in sequential order
_temp_fig_title = None
_temp_point_labels = ['C', 'R']

def get_manual_calibration_points(fig, xy):
    if len(xy) != 2 or xy[0] is None or xy[1] is None:
        return

    global _temp_marker_index
    global _temp_calibration_mapping

    length = len(_temp_point_labels)

    ax = fig.get_axes()[0]
    ann = ax.annotate(_temp_point_labels[_temp_marker_index % length], xy, color='r',
                      fontsize=15)
    print('Manual annotation: ', ann)

    _temp_calibration_mapping.append(xy)
    _temp_marker_index += 1

    update_figure(fig)

    if _temp_marker_index > length - 1:
        print('Manual calibration complete')
        save_figure(_temp_fig_title, fig)
        close_figure(fig)

# return 2 points one related to center and one on a radius of a circular region
def get_selected_points_manually(fig_title, point_labels, eye_gaze_x, eye_gaze_y, eye_gaze_z):
    global _temp_calibration_mapping, _temp_fig_title, _temp_point_labels

    _temp_fig_title = fig_title
    _temp_point_labels = point_labels

    fig = plt.figure()

    ax = plt.gca()

    [x_min, x_max, y_min, y_max, z_min, z_max] = get_visualize_range(eye_gaze_x, eye_gaze_y, eye_gaze_z)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    ax.set_xlabel('x')
    ax.set_ylabel('y')

    maximize_figure()

    plot_scatter(ax, eye_gaze_x, eye_gaze_y, 0)

    ax.grid()

    update_figure(fig)

    cid = fig.canvas.mpl_connect('button_press_event',
                                 lambda event: get_manual_calibration_points(fig, [event.xdata,
                                                                                   event.ydata]))

    display_figure(fig_title, tight=False)
    fig.canvas.mpl_disconnect(cid)

    return np.array(_temp_calibration_mapping)