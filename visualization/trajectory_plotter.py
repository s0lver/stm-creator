from datetime import timedelta
from typing import List

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from mpl_toolkits.mplot3d import art3d

from entities.GpsFix import GpsFix
from entities.StayPoint import StayPoint
from entities.Visit import Visit


def scale_time_value(time_value):
    # one minute = 60
    # one hour = 3600
    # one day = 86400
    return time_value / 86400


def plot_3d_cylinder(current_axis, radius, height, elevation, resolution, color='r', x_center=0, y_center=0):
    x = np.linspace(x_center - radius, x_center + radius, resolution)
    z = np.linspace(elevation, elevation + height, resolution)
    x_mesh, z_mesh = np.meshgrid(x, z)

    y = np.sqrt(radius ** 2 - (x_mesh - x_center) ** 2) + y_center  # Pythagorean theorem

    current_axis.plot_surface(x_mesh, y, z_mesh, linewidth=0, color=color, alpha=0.3)
    current_axis.plot_surface(x_mesh, (2 * y_center - y), z_mesh, linewidth=0, color=color, alpha=0.3)

    floor = Circle((x_center, y_center), radius, color=color)
    current_axis.add_patch(floor)
    art3d.pathpatch_2d_to_3d(floor, z=elevation, zdir="z")

    ceiling = Circle((x_center, y_center), radius, color=color)
    current_axis.add_patch(ceiling)
    art3d.pathpatch_2d_to_3d(ceiling, z=elevation + height, zdir="z")


def plot_trajectories_per_day(ax, fixes):
    rounded_start = fixes[0].timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
    rounded_end = fixes[-1].timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
    days = (rounded_end - rounded_start).days
    start_time = fixes[0].timestamp
    pointer_start = rounded_start
    pointer_end = rounded_start + timedelta(days=1)
    last_fix_previous_day = None
    for i in range(0, days + 1):
        fixes_this_day = list(filter(lambda fix: pointer_start < fix.timestamp < pointer_end, fixes))
        # Try to add one from previous day, if there is any
        if last_fix_previous_day is not None:
            fixes_this_day.insert(0, last_fix_previous_day)

        x = list(map(lambda fix: fix.longitude, fixes_this_day))
        y = list(map(lambda fix: fix.latitude, fixes_this_day))
        z = list(map(lambda fix: scale_time_value(fix.timestamp.timestamp() - start_time.timestamp()),
                     fixes_this_day))

        ax.plot(x, y, z, label='day {} ({})'.format(i + 1, pointer_start.strftime("%A")))
        pointer_start = pointer_end
        pointer_end = pointer_start + timedelta(days=1)
        last_fix_previous_day = fixes_this_day[-1]


def add_visits_cylinders_to_plot(current_axis, visits, stay_points, start_time, spd_min_distance_parameter=500):
    one_degree_in_meters = 101355.14  # according to http://www.csgnetwork.com/gpsdistcalc.html
    radius = (spd_min_distance_parameter / 2.0) / one_degree_in_meters
    resolution = 10

    # colours = plt.cm.Set3(np.linspace(0, 1, 1 + len(stay_points)))
    from brewer2mpl import brewer2mpl
    color_map = brewer2mpl.get_map('Set3', 'qualitative', 12)
    colors = [c for c in color_map.mpl_colors]
    for visit in visits:
        length_visit = (visit.pivot_departure_fix.timestamp - visit.pivot_arrival_fix.timestamp).total_seconds()
        height = scale_time_value(length_visit)
        elevation = scale_time_value(visit.pivot_arrival_fix.timestamp.timestamp() - start_time.timestamp())

        stay_point_id_of_visit = visit.id_stay_point
        stay_point = list(filter(lambda x: x.id_stay_point == stay_point_id_of_visit, stay_points))[0]
        x_center = stay_point.longitude
        y_center = stay_point.latitude

        # color = colours[stay_point_id_of_visit]
        color = colors[stay_point_id_of_visit]

        plot_3d_cylinder(current_axis, radius=radius, height=height, elevation=elevation, resolution=resolution,
                         color=color, x_center=x_center, y_center=y_center)


def plot_from_data(raw_fixes: List[GpsFix], raw_stay_points: List[StayPoint], raw_visits: List[Visit],
                   path_to_save=None):
    plt.style.use('bmh')

    plt.rcParams['font.family'] = 'Gotham XNarrow'
    plt.rcParams['font.serif'] = 'Gotham XNarrow'
    plt.rcParams['font.monospace'] = 'Monaco'
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.labelweight'] = 'normal'
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    # plt.rcParams['legend.fontsize'] = 11
    plt.rcParams['legend.fontsize'] = 7
    plt.rcParams['figure.titlesize'] = 13
    plt.rcParams['legend.fontsize'] = 9
    fig = plt.figure(figsize=(10, 7))
    # fig.suptitle('Trajectory across time', fontsize=14, fontweight='bold')
    axis = fig.gca(projection='3d')

    clean_fixes = list(filter(lambda x: x.is_valid, raw_fixes))
    plot_trajectories_per_day(axis, clean_fixes)

    start_time = clean_fixes[0].timestamp
    add_visits_cylinders_to_plot(axis, raw_visits, raw_stay_points, start_time)

    axis.set_xlabel('Longitude')
    axis.set_ylabel('Latitude')
    axis.set_zlabel('Time (days)')
    axis.zaxis.label.set_rotation(90)
    # axis.zaxis.labelpad = 15

    axis.legend()

    if path_to_save is None:
        fig.show()
    else:
        plt.savefig(path_to_save, format='pdf', dpi=1000)


def plot_trajectory_only(raw_fixes: List[GpsFix]):
    mpl.rcParams['legend.fontsize'] = 8
    fig = plt.figure()
    fig.suptitle('Trajectory across time', fontsize=14, fontweight='bold')
    axis = fig.gca(projection='3d')

    clean_fixes = list(filter(lambda x: x.is_valid, raw_fixes))
    plot_trajectories_per_day(axis, clean_fixes)

    axis.set_xlabel('Longitude')
    axis.set_ylabel('Latitude')
    axis.set_zlabel('Time')
    axis.zaxis.label.set_rotation(90)
    axis.zaxis.labelpad = 15

    axis.legend()
    # plt.show()
    fig.show()


def add_trajectory_to_plot(axis, fixes: List[GpsFix]):
    start_time = fixes[0].timestamp
    x = list(map(lambda fix: fix.longitude, fixes))
    y = list(map(lambda fix: fix.latitude, fixes))
    z = list(map(lambda fix: scale_time_value(fix.timestamp.timestamp() - start_time.timestamp()), fixes))

    axis.plot(x, y, z, marker='o', label='Fixes')


def plot_single_stay_point_visit(stay_point: StayPoint, visit: Visit, raw_fixes: List[GpsFix]):
    mpl.rcParams['legend.fontsize'] = 8
    fig = plt.figure()
    fig.suptitle('Single visit to stay point', fontsize=14, fontweight='bold')
    axis = fig.gca(projection='3d')

    clean_fixes = list(filter(lambda x: x.is_valid, raw_fixes))
    add_trajectory_to_plot(axis, clean_fixes)

    add_visits_cylinders_to_plot(axis, [visit], [stay_point], clean_fixes[0].timestamp)

    axis.set_xlabel('Longitude')
    axis.set_ylabel('Latitude')
    axis.set_zlabel('Time')
    axis.zaxis.label.set_rotation(90)
    axis.zaxis.labelpad = 15

    axis.legend()
    fig.show()
